#!/usr/bin/env python3
"""
This script extracts URLs from "Full URL:" lines of urls.txt.
It performs async DNS/TCP/HTTP checks, latency measurement,
captcha detection, colored output, emoji indicators, retry logic,
user-agent rotation, batch chunking, prints a summary table,
and generates an HTML report.

It now includes:
- Automatic dependency installation for WSL/Ubuntu
- HTML report generation + optional auto-open
"""

import asyncio
import socket
import time
import random
import subprocess
import sys
import importlib
import webbrowser
import aiohttp
import aiodns
from urllib.parse import urlparse
from colorama import Fore, Style, init as colorama_init

colorama_init()

# =========================================================
# AUTO-INSTALL DEPENDENCIES (WSL/Ubuntu)
# =========================================================
REQUIRED_PACKAGES = ["aiohttp", "aiodns", "colorama"]
APT_PACKAGES = ["python3-pip", "python3-dev", "libffi-dev"]

def ensure_packages():
    missing = []

    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return

    print("\n🔧 Missing dependencies detected:", ", ".join(missing))
    print("🔧 Installing required system packages... (sudo may be required)\n")

    try:
        subprocess.run(["sudo", "apt", "update", "-y"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y"] + APT_PACKAGES, check=True)
    except Exception as e:
        print("❌ Failed installing system packages:", e)
        sys.exit(1)

    for pkg in missing:
        print(f"📦 Installing Python package: {pkg}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
        except Exception as e:
            print(f"❌ Failed to install {pkg}: {e}")
            sys.exit(1)

    print("\n✅ Dependencies installed successfully! Restarting script...\n")
    subprocess.run([sys.executable] + sys.argv)
    sys.exit(0)

ensure_packages()

# =========================================================
# CONFIGURATION
# =========================================================
CONCURRENCY       = 30
RETRIES           = 2
DNS_TIMEOUT       = 3
TCP_TIMEOUT       = 3
HTTP_TIMEOUT      = 10
CHUNK_SIZE        = 30

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X)"
]

ICON_OK      = "🟢"
ICON_WARN    = "🟡"
ICON_ERROR   = "🔴"
ICON_CAPTCHA = "🤖"


# =========================================================
# URL NORMALIZER
# =========================================================
def normalize_url(raw):
    raw = raw.strip()
    if not raw:
        return None

    raw = " ".join(raw.split())
    raw = raw.replace(" :", ":").replace(": ", ":")

    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)

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
def load_urls(path):
    entries = []
    current_group = "Ungrouped"

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            if ":" in stripped and not stripped.lower().startswith("full url"):
                current_group = stripped

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
    return entries


# =========================================================
# CAPTCHA DETECTOR
# =========================================================
def detect_captcha(text, headers):
    markers = [
        "captcha", "recaptcha", "hcaptcha", "cloudflare",
        "/cdn-cgi/challenge-platform", "cf-chl"
    ]
    lower = text.lower()
    header_str = " ".join([f"{k}:{v}".lower() for k,v in headers.items()])

    return any(m in lower or m in header_str for m in markers)


# =========================================================
# ASYNC DNS / TCP / HTTP CHECKS
# =========================================================
async def async_dns_lookup(resolver, host):
    for attempt in range(RETRIES+1):
        try:
            start = time.time()
            ans = await asyncio.wait_for(
                resolver.gethostbyname(host, socket.AF_INET),
                timeout=DNS_TIMEOUT
            )
            return ans.addresses[0], None, time.time() - start
        except Exception as e:
            if attempt == RETRIES:
                return None, str(e), None
            await asyncio.sleep(0.2 * (attempt + 1))


async def async_tcp_check(host, port):
    for attempt in range(RETRIES+1):
        try:
            start = time.time()
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=TCP_TIMEOUT
            )
            writer.close()
            await writer.wait_closed()
            return True, None, time.time() - start
        except Exception as e:
            if attempt == RETRIES:
                return False, str(e), None
            await asyncio.sleep(0.2 * (attempt + 1))


async def async_http_check(session, url):
    for attempt in range(RETRIES+1):
        try:
            start = time.time()
            async with session.get(url, timeout=HTTP_TIMEOUT) as resp:
                text = await resp.text(errors="ignore")
                captcha = detect_captcha(text, resp.headers)
                return resp.status, None, captcha, time.time() - start
        except Exception as e:
            if attempt == RETRIES:
                return None, str(e), False, None
            await asyncio.sleep(0.3 * (attempt + 1))


# =========================================================
# FULL URL CHECKER
# =========================================================
async def check_url(entry, resolver, session):
    url = entry["url"]
    parsed = urlparse(url)
    host = parsed.hostname

    try:
        port = parsed.port
    except ValueError:
        port = None
    if not port:
        port = 443 if parsed.scheme == "https" else 80

    dns_ip, dns_err, dns_lat = await async_dns_lookup(resolver, host)

    if not dns_ip:
        return {
            "entry": entry,
            "dns_ip": dns_ip, "dns_err": dns_err, "dns_lat": dns_lat,
            "tcp_ok": None, "tcp_err": None, "tcp_lat": None,
            "http_status": None, "http_err": None, "http_lat": None,
            "captcha": False,
        }

    tcp_ok, tcp_err, tcp_lat = await async_tcp_check(host, port)
    http_status, http_err, captcha, http_lat = await async_http_check(session, url)

    return {
        "entry": entry,
        "dns_ip": dns_ip, "dns_err": dns_err, "dns_lat": dns_lat,
        "tcp_ok": tcp_ok, "tcp_err": tcp_err, "tcp_lat": tcp_lat,
        "http_status": http_status, "http_err": http_err, "http_lat": http_lat,
        "captcha": captcha,
    }


# =========================================================
# COLOR LOGIC
# =========================================================
def colorize(r):
    if r["captcha"]:
        return Fore.YELLOW, ICON_CAPTCHA
    if r["dns_ip"] is None:
        return Fore.RED, ICON_ERROR
    if r["tcp_ok"] is False:
        return Fore.RED, ICON_ERROR
    if r["http_status"] and int(r["http_status"]) >= 400:
        return Fore.RED, ICON_ERROR
    return Fore.GREEN, ICON_OK


# =========================================================
# SUMMARY BUILDER
# =========================================================
def build_summary(results):
    summary = {}
    for r in results:
        group = r["entry"]["group"]
        if group not in summary:
            summary[group] = {"ok":0, "warn":0, "fail":0}

        color, icon = colorize(r)

        if icon == ICON_OK:
            summary[group]["ok"] += 1
        elif icon == ICON_CAPTCHA:
            summary[group]["warn"] += 1
        else:
            summary[group]["fail"] += 1
    return summary


# =========================================================
# HTML REPORT GENERATOR
# =========================================================
def generate_html(results, summary):
    html = []
    html.append("""
    <html>
    <head>
        <style>
            body { font-family: Arial; margin: 20px; }
            .ok { color: green; }
            .warn { color: orange; }
            .fail { color: red; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            td, th { border: 1px solid #aaa; padding: 6px; }
            th { background: #eee; }
        </style>
    </head>
    <body>
    <h1>WebCheck Report</h1>
    """)

    html.append("<h2>Summary</h2><table>")
    html.append("<tr><th>Group</th><th>OK</th><th>Warnings</th><th>Failures</th></tr>")

    for group, data in summary.items():
        html.append(f"<tr><td>{group}</td><td>{data['ok']}</td><td>{data['warn']}</td><td>{data['fail']}</td></tr>")

    html.append("</table><h2>Detailed Results</h2>")

    for r in results:
        e = r["entry"]
        _, icon = colorize(r)

        html.append(f"""
        <h3>{icon} {e['group']}</h3>
        <table>
            <tr><td><b>Original</b></td><td>{e['original']}</td></tr>
            <tr><td><b>URL</b></td><td>{e['url']}</td></tr>
            <tr><td><b>DNS</b></td><td>{r['dns_ip']} ({r['dns_err']})</td></tr>
            <tr><td><b>TCP</b></td><td>{r['tcp_ok']} ({r['tcp_err']})</td></tr>
            <tr><td><b>HTTP</b></td><td>{r['http_status']} ({r['http_err']})</td></tr>
            <tr><td><b>CAPTCHA</b></td><td>{r['captcha']}</td></tr>
        </table>
        """)

    html.append("</body></html>")

    report_path = "webcheck_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    return report_path


# =========================================================
# MAIN EXECUTION
# =========================================================
async def main():
    entries = load_urls("urls.txt")
    resolver = aiodns.DNSResolver()

    connector = aiohttp.TCPConnector(limit=CONCURRENCY, ssl=False)
    async with aiohttp.ClientSession(
        connector=connector,
        headers={"User-Agent": random.choice(USER_AGENTS)}
    ) as session:

        results = []

        for i in range(0, len(entries), CHUNK_SIZE):
            chunk = entries[i : i + CHUNK_SIZE]
            batch = [check_url(e, resolver, session) for e in chunk]

            for fut in asyncio.as_completed(batch):
                r = await fut
                results.append(r)

                color, icon = colorize(r)
                e = r["entry"]

                print("="*60)
                print(color + f"{icon} {e['group']}" + Style.RESET_ALL)
                print(f"Original: {e['original']}")
                print(f"Tested:   {e['url']}")
                print(f"DNS:      {r['dns_ip']} ({r['dns_err']})  Latency={r['dns_lat']}")
                print(f"TCP:      {r['tcp_ok']} ({r['tcp_err']})  Latency={r['tcp_lat']}")
                print(f"HTTP:     {r['http_status']} ({r['http_err']})  Latency={r['http_lat']}")
                print(f"Captcha:  {r['captcha']}")

        # SUMMARY
        print("\n\n" + "#"*60)
        print("SUMMARY TABLE")
        print("#"*60)

        summary = build_summary(results)

        for group, data in summary.items():
            print(f"{group}")
            print(f"  OK:   {data['ok']}")
            print(f"  Warn: {data['warn']}")
            print(f"  Fail: {data['fail']}\n")

        # HTML REPORT
        report_path = generate_html(results, summary)
        print(f"\n📄 HTML report saved to: {report_path}\n")

        # Ask user if they want to open it
        choice = input("Open HTML report now? (y/n): ").strip().lower()
        if choice.startswith("y"):
            webbrowser.open(report_path)
            print("Opening report...")


if __name__ == "__main__":
    asyncio.run(main())
