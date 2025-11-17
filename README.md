# 🌐 WebCheck - High-Performance URL Health Checker

A blazingly fast, production-ready URL health monitoring tool with intelligent rate limiting, anti-fingerprinting, and comprehensive reporting capabilities.

## ✨ Features

### 🚀 Performance
- **Async Architecture** - Concurrent checking using Python asyncio
- **Connection Pooling** - Efficient HTTP session reuse
- **DNS Caching** - 5-minute TTL for faster repeated checks
- **Configurable Concurrency** - Process 30+ URLs simultaneously (default)
- **Batch Processing** - Optimized for large URL lists

### 🛡️ Anti-Detection & Rate Limiting
- **Intelligent Rate Limiting** - Configurable delays with random jitter
- **User-Agent Rotation** - Per-request UA randomization from real browsers
- **Browser-Like Headers** - Full header suite mimicking Chrome/Firefox/Safari
- **Jitter Implementation** - Randomized timing to avoid pattern detection
- **Connection Reuse** - Reduces fingerprinting via consistent connections

### 🔍 Comprehensive Checks
- **DNS Resolution** - Verify domain resolution with latency measurement
- **TCP Connectivity** - Test port reachability
- **HTTP/HTTPS** - Full request with status code validation
- **CAPTCHA Detection** - Identify Cloudflare, reCAPTCHA, hCAPTCHA challenges
- **SSL Verification** - Configurable certificate validation
- **Retry Logic** - Exponential backoff with configurable attempts

### 📊 Reporting & Output
- **HTML Reports** - Beautiful, responsive reports with styling
- **JSON Export** - Machine-readable structured data
- **CSV Export** - Spreadsheet-compatible format
- **Real-time Console** - Color-coded output with emoji indicators
- **Progress Bar** - Visual feedback with ETA
- **Error-Only Mode** - Filter to show only failures
- **Grouped Results** - Organized by URL categories
- **Latency Metrics** - DNS, TCP, and HTTP timing data

### ⚙️ Configuration & Flexibility
- **CLI Arguments** - Override any setting from command line
- **Config Files** - YAML/JSON configuration support
- **Verbose Logging** - Debug mode with detailed logs
- **Type Safety** - Python dataclasses for structured results
- **Extensible** - Clean, modular architecture

## 🔧 Installation

### Requirements
- Python 3.7+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install aiohttp aiodns colorama tqdm pyyaml
```

## 📖 Usage

### Basic Usage
```bash
python webcheck.py urls.txt
```

### Advanced Examples

**Export to multiple formats:**
```bash
python webcheck.py urls.txt --json --csv --html
```

**Show only failures:**
```bash
python webcheck.py urls.txt --error-only
```

**High-speed checking (with caution):**
```bash
python webcheck.py urls.txt --concurrency 100 --rate-limit 0.05
```

**Use configuration file:**
```bash
python webcheck.py urls.txt --config config.yaml
```

**Verbose debug mode:**
```bash
python webcheck.py urls.txt --verbose
```

**Disable SSL verification (not recommended):**
```bash
python webcheck.py urls.txt --no-ssl-verify
```

**Custom output filename:**
```bash
python webcheck.py urls.txt --output my_report --json --csv
```

## 📝 Input File Format

WebCheck supports grouped URL lists with the following format:

```
Group Name 1: Description
  Full URL: https://example.com/path
  Full URL: https://another-example.com

Group Name 2: Another Description
  Full URL: https://third-example.com
```

**Key points:**
- Lines with `:` (but not starting with "Full URL:") are treated as group headers
- Lines starting with "Full URL:" are extracted and checked
- URLs without `http://` or `https://` are automatically prefixed with `https://`
- Malformed URLs are skipped with warnings

## ⚙️ Configuration

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Input file containing URLs | Required |
| `--config`, `-c` | Configuration file (YAML/JSON) | None |
| `--concurrency` | Number of concurrent connections | 30 |
| `--retries` | Number of retries per check | 3 |
| `--timeout` | HTTP timeout in seconds | 10.0 |
| `--rate-limit` | Delay between requests (seconds) | 0.1 |
| `--no-ssl-verify` | Disable SSL verification | False |
| `--error-only` | Show only failed checks | False |
| `--verbose`, `-v` | Verbose output with debug info | False |
| `--json` | Export to JSON | False |
| `--csv` | Export to CSV | False |
| `--html` | Export to HTML | True |
| `--output`, `-o` | Output filename (without extension) | webcheck_report |

### Configuration File

Create a `config.yaml` file:

```yaml
concurrency: 30
retries: 3
dns_timeout: 3.0
tcp_timeout: 3.0
http_timeout: 10.0
rate_limit_delay: 0.1
jitter_max: 0.3
ssl_verify: true
error_only: false
verbose: false
```

Or use JSON format (`config.json`):

```json
{
  "concurrency": 30,
  "retries": 3,
  "rate_limit_delay": 0.1,
  "jitter_max": 0.3,
  "ssl_verify": true
}
```

## 🎯 Use Cases

### 1. Website Monitoring
Monitor multiple websites for availability:
```bash
python webcheck.py production-sites.txt --error-only
```

### 2. Load Testing Preparation
Verify endpoints before load testing:
```bash
python webcheck.py api-endpoints.txt --concurrency 50 --json
```

### 3. Migration Validation
Check URLs after DNS changes:
```bash
python webcheck.py migration-urls.txt --csv --html
```

### 4. Compliance Checking
Verify SSL certificates on all domains:
```bash
python webcheck.py domains.txt --verbose
```

### 5. Bulk URL Validation
Validate large lists of URLs:
```bash
python webcheck.py bulk-urls.txt --concurrency 100 --rate-limit 0.05 --json
```

## 📊 Output Formats

### Console Output
```
============================================================
🟢 AK (Alaska): www.commerce.alaska.gov
Original: Full URL: https://www.commerce.alaska.gov/cbp/main
Tested:   https://www.commerce.alaska.gov/cbp/main
DNS:      192.0.2.1 (0.045s)
TCP:      True (0.123s)
HTTP:     200 (0.456s)
```

### HTML Report
Beautiful, responsive HTML with:
- Summary table with statistics
- Detailed results per URL
- Color-coded status indicators
- Clickable URLs
- Latency information

### JSON Export
```json
{
  "timestamp": "2025-11-17 12:00:00",
  "total_urls": 51,
  "results": [
    {
      "group": "AK (Alaska)",
      "url": "https://commerce.alaska.gov",
      "dns_ip": "192.0.2.1",
      "http_status": 200,
      "captcha": false
    }
  ]
}
```

### CSV Export
Spreadsheet-compatible format with columns:
- Group, URL, Original, DNS_IP, DNS_Error, DNS_Latency
- TCP_OK, TCP_Error, TCP_Latency
- HTTP_Status, HTTP_Error, HTTP_Latency
- Captcha, Success

## 🔒 Security Features

### SSL Verification
- Enabled by default
- Validates certificate chains
- Prevents MITM attacks
- Can be disabled for testing only

### No Auto-Sudo
- Manual dependency installation required
- No elevated privileges
- User maintains control

### Safe Defaults
- Reasonable concurrency limits
- Rate limiting enabled
- Timeout protections
- Error handling throughout

## 🚦 Rate Limiting Best Practices

### Avoid CDN Blocks
```bash
# Conservative (safe for most sites)
python webcheck.py urls.txt --rate-limit 0.2 --concurrency 20

# Moderate (balanced speed/safety)
python webcheck.py urls.txt --rate-limit 0.1 --concurrency 30

# Aggressive (use with caution)
python webcheck.py urls.txt --rate-limit 0.05 --concurrency 50
```

### Jitter Implementation
WebCheck automatically adds random jitter (0-0.3s by default) to prevent pattern detection by CDNs and WAFs.

### User-Agent Rotation
Per-request rotation through 7 real browser user agents:
- Chrome (Windows, macOS, Linux)
- Firefox (Linux)
- Safari (macOS, iOS)
- Edge (Windows)

## 🐛 Troubleshooting

### Import Errors
```bash
pip install --upgrade aiohttp aiodns colorama tqdm pyyaml
```

### SSL Errors
```bash
# For self-signed certificates (testing only)
python webcheck.py urls.txt --no-ssl-verify
```

### Rate Limiting Issues
```bash
# Increase delay and reduce concurrency
python webcheck.py urls.txt --rate-limit 0.5 --concurrency 10
```

### DNS Resolution Failures
- Check your DNS server configuration
- Verify network connectivity
- Try increasing timeout: `--timeout 20`

## 📈 Performance Tips

1. **Optimize Concurrency**: Start with 30, increase gradually
2. **Use Rate Limiting**: Prevent blocks with `--rate-limit`
3. **Filter Output**: Use `--error-only` for large lists
4. **Enable DNS Caching**: Automatic 5-minute TTL
5. **Reuse Connections**: Built-in connection pooling

## 🛠️ Development

### Architecture
- **Async/Await**: Full asyncio implementation
- **Type Hints**: Complete type annotations
- **Dataclasses**: Structured result types
- **Modular Design**: Clean separation of concerns
- **Logging**: Comprehensive debug logging

### Code Structure
```
webcheck.py
├── Configuration (Config dataclass)
├── URL Loading & Normalization
├── DNS/TCP/HTTP Check Functions
├── Rate Limiting (RateLimiter class)
├── CAPTCHA Detection
├── Result Handling (CheckResult dataclass)
├── Export Functions (HTML/JSON/CSV)
└── Main Execution
```

## 📄 License

This project is provided as-is for URL health checking and monitoring purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional export formats
- Enhanced CAPTCHA detection
- Proxy support
- WebSocket checking
- Custom headers per URL
- Screenshot capture
- Response time trending

## ⚠️ Disclaimer

This tool is designed for legitimate website monitoring and health checking. Users are responsible for:
- Respecting robots.txt
- Following website terms of service
- Avoiding excessive requests
- Using appropriate rate limiting

## 🎓 Credits

Built with:
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
- [aiodns](https://github.com/saghul/aiodns) - Async DNS resolver
- [colorama](https://github.com/tartley/colorama) - Cross-platform colored terminal output
- [tqdm](https://github.com/tqdm/tqdm) - Progress bar library
- [PyYAML](https://pyyaml.org/) - YAML parser

---

**Made for high-performance URL health checking with anti-detection capabilities.**
