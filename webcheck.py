#!/usr/bin/env python3
"""
WebCheck - High-Performance URL Health Checker
Performs async DNS/TCP/HTTP checks with intelligent rate limiting,
captcha detection, latency measurement, and comprehensive reporting.

Features:
- Async concurrent checking with configurable limits
- Intelligent rate limiting with jitter to avoid CDN blocks
- Per-request user-agent and header rotation for anti-fingerprinting
- Progress bar and real-time status updates
- Multiple export formats (HTML, JSON, CSV)
- Colored console output with emoji indicators
- Retry logic with exponential backoff
- Connection pooling and session reuse
- Error-only view mode
- Comprehensive logging
- YAML/JSON configuration file support
"""

import asyncio
import socket
import time
import random
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass, asdict

try:
    import aiohttp
    import aiodns
    from colorama import Fore, Style, init as colorama_init
    from tqdm.asyncio import tqdm as async_tqdm
    import yaml
except ImportError as e:
    print(f"❌ Missing required dependency: {e.name}")
    print("\nPlease install dependencies:")
    print("  pip install aiohttp aiodns colorama tqdm pyyaml")
    sys.exit(1)

colorama_init()

# =========================================================
# CONFIGURATION
# =========================================================
@dataclass
class Config:
    concurrency: int = 30
    retries: int = 3
    dns_timeout: float = 3.0
    tcp_timeout: float = 3.0
    http_timeout: float = 10.0
    rate_limit_delay: float = 0.1  # Delay between requests (seconds)
    jitter_max: float = 0.3  # Random jitter to avoid pattern detection
    ssl_verify: bool = True
    error_only: bool = False
    verbose: bool = False

    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        """Load configuration from YAML or JSON file"""
        if not path.exists():
            return cls()

        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

# Enhanced user agents list - mimics real browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
]

# Browser-like headers for anti-fingerprinting
BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

ICON_OK = "🟢"
ICON_WARN = "🟡"
ICON_ERROR = "🔴"
ICON_CAPTCHA = "🤖"

# =========================================================
# LOGGING SETUP
# =========================================================
def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('webcheck.log'),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = logging.getLogger(__name__)

# =========================================================
# DATA STRUCTURES
# =========================================================
@dataclass
class CheckResult:
    """Result of a URL check"""
    group: str
    original: str
    url: str
    dns_ip: Optional[str]
    dns_error: Optional[str]
    dns_latency: Optional[float]
    tcp_ok: Optional[bool]
    tcp_error: Optional[str]
    tcp_latency: Optional[float]
    http_status: Optional[int]
    http_error: Optional[str]
    http_latency: Optional[float]
    captcha: bool

    def is_success(self) -> bool:
        """Check if URL is healthy"""
        return (self.dns_ip is not None and
                self.tcp_ok is True and
                self.http_status is not None and
                self.http_status < 400 and
                not self.captcha)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

# =========================================================
# URL NORMALIZER
# =========================================================
def normalize_url(raw: str) -> Optional[str]:
    """Normalize and validate URL"""
    raw = raw.strip()
    if not raw:
        return None

    # Clean whitespace
    raw = " ".join(raw.split())
    raw = raw.replace(" :", ":").replace(": ", ":")

    # Add scheme if missing
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)

    # Handle invalid port
    try:
        _ = parsed.port
    except ValueError:
        host = parsed.hostname
        if not host:
            return None
        raw = f"{parsed.scheme}://{host}{parsed.path or ''}"
        parsed = urlparse(raw)

    return raw if parsed.hostname else None

# =========================================================
# LOAD URLS & PRESERVE GROUP LABELS
# =========================================================
def load_urls(path: str) -> List[Dict]:
    """Load URLs from file and preserve group labels"""
    entries = []
    current_group = "Ungrouped"

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()

                # Detect group headers
                if ":" in stripped and not stripped.lower().startswith("full url"):
                    current_group = stripped

                # Extract URLs from "Full URL:" lines
                if stripped.lower().startswith("full url:"):
                    original = stripped
                    raw = stripped.split(":", 1)[1].strip()
                    norm = normalize_url(raw)

                    if norm:
                        entries.append({
                            "group": current_group,
                            "original": original,
                            "raw": raw,
                            "url": norm
                        })

        logger.info(f"Loaded {len(entries)} URLs from {path}")
        return entries

    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        print(f"❌ Error: File '{path}' not found")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading URLs: {e}")
        print(f"❌ Error loading URLs: {e}")
        sys.exit(1)

# =========================================================
# CAPTCHA DETECTOR
# =========================================================
def detect_captcha(text: str, headers: dict) -> bool:
    """Detect if response contains captcha challenge"""
    markers = [
        "captcha", "recaptcha", "hcaptcha", "cloudflare",
        "/cdn-cgi/challenge-platform", "cf-chl", "cf-ray",
        "access denied", "rate limit", "too many requests",
        "human verification", "security check"
    ]
    lower = text.lower()
    header_str = " ".join([f"{k}:{v}".lower() for k, v in headers.items()])

    return any(m in lower or m in header_str for m in markers)

# =========================================================
# INTELLIGENT RATE LIMITER
# =========================================================
class RateLimiter:
    """Intelligent rate limiter with jitter"""
    def __init__(self, delay: float, jitter: float):
        self.delay = delay
        self.jitter = jitter
        self.last_request = 0.0

    async def wait(self):
        """Wait with jitter to avoid detection patterns"""
        now = time.time()
        elapsed = now - self.last_request
        wait_time = self.delay - elapsed

        if wait_time > 0:
            # Add random jitter
            jitter = random.uniform(0, self.jitter)
            await asyncio.sleep(wait_time + jitter)

        self.last_request = time.time()

# =========================================================
# HEADER ROTATION
# =========================================================
def get_random_headers() -> dict:
    """Generate randomized browser-like headers"""
    headers = BROWSER_HEADERS.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)

    # Randomize accept-language
    langs = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en;q=0.9"]
    headers["Accept-Language"] = random.choice(langs)

    return headers

# =========================================================
# ASYNC DNS / TCP / HTTP CHECKS
# =========================================================
async def async_dns_lookup(resolver: aiodns.DNSResolver, host: str, retries: int) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """Async DNS lookup with retry"""
    for attempt in range(retries + 1):
        try:
            start = time.time()
            ans = await asyncio.wait_for(
                resolver.gethostbyname(host, socket.AF_INET),
                timeout=3.0
            )
            latency = time.time() - start
            logger.debug(f"DNS OK: {host} -> {ans.addresses[0]} ({latency:.3f}s)")
            return ans.addresses[0], None, latency
        except asyncio.TimeoutError:
            err = "DNS timeout"
            if attempt == retries:
                logger.warning(f"DNS failed: {host} - {err}")
                return None, err, None
        except Exception as e:
            err = str(e)
            if attempt == retries:
                logger.warning(f"DNS failed: {host} - {err}")
                return None, err, None

        # Exponential backoff with jitter
        await asyncio.sleep(0.2 * (2 ** attempt) + random.uniform(0, 0.1))

    return None, "Unknown error", None


async def async_tcp_check(host: str, port: int, retries: int) -> Tuple[bool, Optional[str], Optional[float]]:
    """Async TCP connection check with retry"""
    for attempt in range(retries + 1):
        try:
            start = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=3.0
            )
            latency = time.time() - start

            writer.close()
            await writer.wait_closed()

            logger.debug(f"TCP OK: {host}:{port} ({latency:.3f}s)")
            return True, None, latency
        except asyncio.TimeoutError:
            err = "TCP timeout"
            if attempt == retries:
                logger.warning(f"TCP failed: {host}:{port} - {err}")
                return False, err, None
        except Exception as e:
            err = str(e)
            if attempt == retries:
                logger.warning(f"TCP failed: {host}:{port} - {err}")
                return False, err, None

        await asyncio.sleep(0.2 * (2 ** attempt) + random.uniform(0, 0.1))

    return False, "Unknown error", None


async def async_http_check(session: aiohttp.ClientSession, url: str, retries: int, rate_limiter: RateLimiter) -> Tuple[Optional[int], Optional[str], bool, Optional[float]]:
    """Async HTTP check with retry and rate limiting"""
    for attempt in range(retries + 1):
        try:
            # Apply rate limiting with jitter
            await rate_limiter.wait()

            start = time.time()

            # Rotate headers per request
            headers = get_random_headers()

            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10.0)) as resp:
                text = await resp.text(errors="ignore")
                latency = time.time() - start
                captcha = detect_captcha(text, dict(resp.headers))

                logger.debug(f"HTTP {resp.status}: {url} ({latency:.3f}s) captcha={captcha}")
                return resp.status, None, captcha, latency

        except asyncio.TimeoutError:
            err = "HTTP timeout"
            if attempt == retries:
                logger.warning(f"HTTP failed: {url} - {err}")
                return None, err, False, None
        except Exception as e:
            err = str(e)
            if attempt == retries:
                logger.warning(f"HTTP failed: {url} - {err}")
                return None, err, False, None

        await asyncio.sleep(0.3 * (2 ** attempt) + random.uniform(0, 0.2))

    return None, "Unknown error", False, None

# =========================================================
# FULL URL CHECKER
# =========================================================
async def check_url(entry: Dict, resolver: aiodns.DNSResolver, session: aiohttp.ClientSession, config: Config, rate_limiter: RateLimiter) -> CheckResult:
    """Perform complete URL health check"""
    url = entry["url"]
    parsed = urlparse(url)
    host = parsed.hostname

    # Determine port
    try:
        port = parsed.port
    except ValueError:
        port = None
    if not port:
        port = 443 if parsed.scheme == "https" else 80

    # DNS lookup
    dns_ip, dns_err, dns_lat = await async_dns_lookup(resolver, host, config.retries)

    if not dns_ip:
        return CheckResult(
            group=entry["group"],
            original=entry["original"],
            url=url,
            dns_ip=dns_ip,
            dns_error=dns_err,
            dns_latency=dns_lat,
            tcp_ok=None,
            tcp_error=None,
            tcp_latency=None,
            http_status=None,
            http_error=None,
            http_latency=None,
            captcha=False,
        )

    # TCP check
    tcp_ok, tcp_err, tcp_lat = await async_tcp_check(host, port, config.retries)

    # HTTP check
    http_status, http_err, captcha, http_lat = await async_http_check(session, url, config.retries, rate_limiter)

    return CheckResult(
        group=entry["group"],
        original=entry["original"],
        url=url,
        dns_ip=dns_ip,
        dns_error=dns_err,
        dns_latency=dns_lat,
        tcp_ok=tcp_ok,
        tcp_error=tcp_err,
        tcp_latency=tcp_lat,
        http_status=http_status,
        http_error=http_err,
        http_latency=http_lat,
        captcha=captcha,
    )

# =========================================================
# COLOR LOGIC
# =========================================================
def colorize(result: CheckResult) -> Tuple[str, str]:
    """Determine color and icon for result"""
    if result.captcha:
        return Fore.YELLOW, ICON_CAPTCHA
    if result.dns_ip is None:
        return Fore.RED, ICON_ERROR
    if result.tcp_ok is False:
        return Fore.RED, ICON_ERROR
    if result.http_status and result.http_status >= 400:
        return Fore.RED, ICON_ERROR
    return Fore.GREEN, ICON_OK

# =========================================================
# DISPLAY OUTPUT
# =========================================================
def print_result(result: CheckResult, verbose: bool = False):
    """Print result to console"""
    color, icon = colorize(result)

    print("=" * 60)
    print(color + f"{icon} {result.group}" + Style.RESET_ALL)
    print(f"Original: {result.original}")
    print(f"Tested:   {result.url}")

    if verbose or result.dns_error:
        print(f"DNS:      {result.dns_ip or 'FAILED'} (err={result.dns_error})  Latency={result.dns_latency:.3f}s" if result.dns_latency else f"DNS:      {result.dns_ip or 'FAILED'} (err={result.dns_error})")
    else:
        print(f"DNS:      {result.dns_ip} ({result.dns_latency:.3f}s)" if result.dns_latency else f"DNS:      {result.dns_ip}")

    if verbose or result.tcp_error:
        print(f"TCP:      {result.tcp_ok} (err={result.tcp_error})  Latency={result.tcp_latency:.3f}s" if result.tcp_latency else f"TCP:      {result.tcp_ok} (err={result.tcp_error})")
    else:
        print(f"TCP:      {result.tcp_ok} ({result.tcp_latency:.3f}s)" if result.tcp_latency else f"TCP:      {result.tcp_ok}")

    if verbose or result.http_error:
        print(f"HTTP:     {result.http_status or 'FAILED'} (err={result.http_error})  Latency={result.http_latency:.3f}s" if result.http_latency else f"HTTP:     {result.http_status or 'FAILED'} (err={result.http_error})")
    else:
        print(f"HTTP:     {result.http_status} ({result.http_latency:.3f}s)" if result.http_latency else f"HTTP:     {result.http_status}")

    if result.captcha:
        print(color + "⚠️  CAPTCHA DETECTED" + Style.RESET_ALL)

# =========================================================
# SUMMARY BUILDER
# =========================================================
def build_summary(results: List[CheckResult]) -> Dict[str, Dict[str, int]]:
    """Build summary statistics"""
    summary = {}
    for r in results:
        group = r.group
        if group not in summary:
            summary[group] = {"ok": 0, "warn": 0, "fail": 0}

        _, icon = colorize(r)

        if icon == ICON_OK:
            summary[group]["ok"] += 1
        elif icon == ICON_CAPTCHA:
            summary[group]["warn"] += 1
        else:
            summary[group]["fail"] += 1

    return summary

# =========================================================
# EXPORT FUNCTIONS
# =========================================================
def export_json(results: List[CheckResult], filepath: str):
    """Export results to JSON"""
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_urls": len(results),
        "results": [r.to_dict() for r in results]
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON report saved to {filepath}")
    print(f"📄 JSON report saved to: {filepath}")


def export_csv(results: List[CheckResult], filepath: str):
    """Export results to CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Group", "URL", "Original", "DNS_IP", "DNS_Error", "DNS_Latency",
            "TCP_OK", "TCP_Error", "TCP_Latency", "HTTP_Status", "HTTP_Error",
            "HTTP_Latency", "Captcha", "Success"
        ])

        # Data
        for r in results:
            writer.writerow([
                r.group, r.url, r.original, r.dns_ip, r.dns_error or "",
                f"{r.dns_latency:.3f}" if r.dns_latency else "",
                r.tcp_ok, r.tcp_error or "",
                f"{r.tcp_latency:.3f}" if r.tcp_latency else "",
                r.http_status, r.http_error or "",
                f"{r.http_latency:.3f}" if r.http_latency else "",
                r.captcha, r.is_success()
            ])

    logger.info(f"CSV report saved to {filepath}")
    print(f"📄 CSV report saved to: {filepath}")


def export_html(results: List[CheckResult], summary: Dict, filepath: str):
    """Export results to HTML"""
    html = []
    html.append("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>WebCheck Report</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                margin: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }
            h2 { color: #555; margin-top: 30px; }
            .ok { color: #4CAF50; font-weight: bold; }
            .warn { color: #FF9800; font-weight: bold; }
            .fail { color: #f44336; font-weight: bold; }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            td, th {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
                color: #333;
            }
            tr:hover { background: #f8f9fa; }
            .detail-group {
                margin: 20px 0;
                padding: 15px;
                border-left: 4px solid #4CAF50;
                background: #f9f9f9;
            }
            .timestamp {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
    <div class="container">
    <h1>🌐 WebCheck Report</h1>
    <div class="timestamp">Generated: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</div>
    """)

    # Summary table
    html.append("<h2>📊 Summary</h2><table>")
    html.append("<tr><th>Group</th><th>✅ OK</th><th>⚠️ Warnings</th><th>❌ Failures</th><th>Total</th></tr>")

    for group, data in summary.items():
        total = data['ok'] + data['warn'] + data['fail']
        html.append(f"<tr><td><strong>{group}</strong></td><td class='ok'>{data['ok']}</td><td class='warn'>{data['warn']}</td><td class='fail'>{data['fail']}</td><td>{total}</td></tr>")

    html.append("</table>")

    # Detailed results
    html.append("<h2>🔍 Detailed Results</h2>")

    for r in results:
        _, icon = colorize(r)
        status_class = "ok" if r.is_success() else ("warn" if r.captcha else "fail")

        html.append(f"""
        <div class="detail-group">
            <h3 class="{status_class}">{icon} {r.group}</h3>
            <table>
                <tr><td><b>Original</b></td><td>{r.original}</td></tr>
                <tr><td><b>URL</b></td><td><a href="{r.url}" target="_blank">{r.url}</a></td></tr>
                <tr><td><b>DNS</b></td><td>{r.dns_ip or 'FAILED'} {f'({r.dns_error})' if r.dns_error else ''} {f'<span style="color:#888">({r.dns_latency:.3f}s)</span>' if r.dns_latency else ''}</td></tr>
                <tr><td><b>TCP</b></td><td>{r.tcp_ok} {f'({r.tcp_error})' if r.tcp_error else ''} {f'<span style="color:#888">({r.tcp_latency:.3f}s)</span>' if r.tcp_latency else ''}</td></tr>
                <tr><td><b>HTTP</b></td><td>{r.http_status or 'FAILED'} {f'({r.http_error})' if r.http_error else ''} {f'<span style="color:#888">({r.http_latency:.3f}s)</span>' if r.http_latency else ''}</td></tr>
                <tr><td><b>CAPTCHA</b></td><td class="{'warn' if r.captcha else 'ok'}">{r.captcha}</td></tr>
            </table>
        </div>
        """)

    html.append("</div></body></html>")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(html))

    logger.info(f"HTML report saved to {filepath}")
    print(f"📄 HTML report saved to: {filepath}")

# =========================================================
# MAIN EXECUTION
# =========================================================
async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="WebCheck - High-Performance URL Health Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s urls.txt                          # Basic check with HTML report
  %(prog)s urls.txt --json --csv             # Export to JSON and CSV
  %(prog)s urls.txt --error-only             # Show only failures
  %(prog)s urls.txt --concurrency 50         # Use 50 concurrent connections
  %(prog)s urls.txt --config config.yaml    # Load config from file
  %(prog)s urls.txt --no-ssl-verify          # Disable SSL verification (not recommended)
        """
    )

    parser.add_argument("input_file", help="Input file containing URLs")
    parser.add_argument("--config", "-c", help="Configuration file (YAML/JSON)")
    parser.add_argument("--concurrency", type=int, help="Number of concurrent connections")
    parser.add_argument("--retries", type=int, help="Number of retries per check")
    parser.add_argument("--timeout", type=float, help="HTTP timeout in seconds")
    parser.add_argument("--rate-limit", type=float, help="Delay between requests (seconds)")
    parser.add_argument("--no-ssl-verify", action="store_true", help="Disable SSL verification")
    parser.add_argument("--error-only", action="store_true", help="Show only failed checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with debug info")
    parser.add_argument("--json", action="store_true", help="Export to JSON")
    parser.add_argument("--csv", action="store_true", help="Export to CSV")
    parser.add_argument("--html", action="store_true", default=True, help="Export to HTML (default)")
    parser.add_argument("--output", "-o", default="webcheck_report", help="Output filename (without extension)")

    args = parser.parse_args()

    # Load configuration
    if args.config:
        config = Config.from_file(Path(args.config))
    else:
        config = Config()

    # Override with CLI arguments
    if args.concurrency:
        config.concurrency = args.concurrency
    if args.retries:
        config.retries = args.retries
    if args.timeout:
        config.http_timeout = args.timeout
    if args.rate_limit:
        config.rate_limit_delay = args.rate_limit
    if args.no_ssl_verify:
        config.ssl_verify = False
    if args.error_only:
        config.error_only = True
    if args.verbose:
        config.verbose = True

    # Setup logging
    global logger
    logger = setup_logging(config.verbose)

    logger.info("=" * 60)
    logger.info("WebCheck started")
    logger.info(f"Config: concurrency={config.concurrency}, retries={config.retries}, ssl_verify={config.ssl_verify}")

    # Header with emoji-aware width (emojis take 2 columns)
    print("\n" + "=" * 70)
    print("  🌐 WebCheck - High-Performance URL Health Checker")
    print("=" * 70)
    print(f"  ⚙️  Concurrency: {config.concurrency} | Retries: {config.retries} | SSL: {config.ssl_verify}")
    print(f"  ⏱️  Rate limit: {config.rate_limit_delay}s + jitter")
    print("=" * 70 + "\n")

    # Load URLs
    entries = load_urls(args.input_file)

    if not entries:
        print("❌ No valid URLs found in input file")
        sys.exit(1)

    print(f"📋 Loaded {len(entries)} URLs\n")

    # Create DNS resolver
    resolver = aiodns.DNSResolver()

    # Create rate limiter
    rate_limiter = RateLimiter(config.rate_limit_delay, config.jitter_max)

    # Create HTTP session with connection pooling
    connector = aiohttp.TCPConnector(
        limit=config.concurrency,
        ssl=config.ssl_verify,
        ttl_dns_cache=300,  # Cache DNS for 5 minutes
        force_close=False,   # Reuse connections
    )

    results = []

    async with aiohttp.ClientSession(connector=connector) as session:
        # Create tasks
        tasks = [check_url(e, resolver, session, config, rate_limiter) for e in entries]

        # Execute with progress bar
        print("🔍 Checking URLs...\n")

        for coro in async_tqdm.as_completed(tasks, total=len(tasks), desc="Progress", unit="url"):
            result = await coro
            results.append(result)

            # Print result if not error-only mode, or if error-only and it's an error
            if not config.error_only or not result.is_success():
                print_result(result, config.verbose)

    # Build summary
    summary = build_summary(results)

    # Print summary
    print("\n\n" + "#" * 60)
    print("📊 SUMMARY")
    print("#" * 60)

    total_ok = sum(s['ok'] for s in summary.values())
    total_warn = sum(s['warn'] for s in summary.values())
    total_fail = sum(s['fail'] for s in summary.values())

    print(f"\n🌐 Total URLs: {len(results)}")
    print(f"✅ Success: {total_ok} ({total_ok/len(results)*100:.1f}%)")
    print(f"⚠️  Warnings: {total_warn} ({total_warn/len(results)*100:.1f}%)")
    print(f"❌ Failures: {total_fail} ({total_fail/len(results)*100:.1f}%)")
    print()

    for group, data in summary.items():
        print(f"\n{group}")
        print(f"  ✅ OK:   {data['ok']}")
        print(f"  ⚠️  Warn: {data['warn']}")
        print(f"  ❌ Fail: {data['fail']}")

    # Export reports
    print("\n" + "#" * 60)
    print("📄 EXPORTING REPORTS")
    print("#" * 60 + "\n")

    if args.html:
        export_html(results, summary, f"{args.output}.html")

    if args.json:
        export_json(results, f"{args.output}.json")

    if args.csv:
        export_csv(results, f"{args.output}.csv")

    logger.info("WebCheck completed successfully")
    print("\n✅ All checks completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception("Fatal error")
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
