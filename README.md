# 🌐 WebCheck - The URL Health Checker That Doesn't Suck

> *Because life's too short for broken links and slow monitoring tools* 🚀

A **blazingly fast**, production-ready URL health monitoring tool that actually works. No enterprise bloat. No confusing dashboards. Just pure, async, Python-powered URL checking goodness with intelligent rate limiting, anti-fingerprinting, and reports so pretty they'll make you cry. 😭

**Run Anywhere:** CLI • Web Browser • Cloud Shell | **Check Everything:** DNS • TCP • HTTP • SSL • CAPTCHA Detection

<p align="center">
  <a href="https://www.buymeacoffee.com/diatasso" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 180px !important;" >
  </a>
</p>

<p align="center">
  <strong>⭐ Star us if we saved your sanity! ⭐</strong>
</p>

---

## 🎯 What Makes WebCheck Different?

Most URL checkers are either:
- 💸 Expensive SaaS platforms that cost more than your lunch
- 🐌 Slow as molasses (seriously, who has time for this?)
- 🤖 Easily blocked by CDNs and rate limiters
- 😵‍💫 So complicated they need a PhD to configure

**WebCheck is:**
- ⚡ **FAST** - Async from the ground up, checks 30+ URLs simultaneously
- 🧠 **SMART** - Intelligent rate limiting with random jitter (CDNs can't pattern-match us!)
- 🎨 **BEAUTIFUL** - HTML reports that don't look like they're from 1995
- 🆓 **FREE** - MIT licensed, no paywalls, no "enterprise features"
- 🌍 **EVERYWHERE** - CLI, Web, Cloud Shell - your choice!

---

## ✨ Features That'll Make You Smile

### 🚀 Performance (Because Waiting Sucks)
- **Async Architecture** - Python asyncio doing the heavy lifting
- **Connection Pooling** - Reuse HTTP sessions like a boss
- **DNS Caching** - 5-minute TTL (why resolve twice?)
- **30+ Concurrent Checks** - Configurable up to 100 (if you're brave)
- **Progress Bar** - Watch the magic happen in real-time

### 🛡️ Anti-Detection Magic (Stealth Mode: ON)
- **Intelligent Rate Limiting** - Configurable delays + random jitter
- **User-Agent Rotation** - 7 real browser UAs, rotated per request
- **Browser-Like Headers** - Full header suite (Accept, DNT, Sec-Fetch-*, etc.)
- **Jitter Implementation** - Random timing defeats pattern detection
- **Connection Reuse** - Look like a real browser, not a bot

### 🔍 Checks Everything (Seriously, Everything)
- **DNS Resolution** - Is it even a real domain? ✅
- **TCP Connectivity** - Can we reach it? ✅
- **HTTP/HTTPS** - Does it respond? ✅
- **CAPTCHA Detection** - Cloudflare, reCAPTCHA, hCAPTCHA - we see you! 🤖
- **SSL Verification** - Trust but verify 🔒
- **Latency Metrics** - How fast is it really? ⏱️

### 📊 Reporting (The Good Stuff)
- **HTML Reports** - Responsive, beautiful, actually readable
- **JSON Export** - For your APIs and data pipelines
- **CSV Export** - Excel-compatible (for the spreadsheet folks)
- **Real-time Console** - Color-coded emoji goodness 🟢🟡🔴
- **Error-Only Mode** - Filter the noise, see the problems
- **Grouped Results** - Organize by categories automatically

### ⚙️ Configuration (Your Way)
- **CLI Arguments** - Override anything from command line
- **Config Files** - YAML/JSON configuration support
- **Verbose Logging** - Debug mode when things go sideways
- **Type Safety** - Python dataclasses for the win
- **No Auto-Sudo** - We respect your security posture

---

## 🚀 Installation (Under 1 Minute, We Promise)

### Requirements
- Python 3.7+ (if you're on 2.7, we need to talk)
- pip (probably already have it)

### Quick Install
```bash
git clone https://github.com/shadowdevnotreal/URL-Check
cd URL-Check
pip install -r requirements.txt
```

**That's it!** No Docker. No Kubernetes. No sacrificing goats to the DevOps gods. Just Python. 🐍

### Web Interface (Optional)
Want the browser UI? Add this:
```bash
pip install flask flask-cors
```

---

## 🎮 Three Ways to Play

### 1️⃣ **Command Line** (For the Cool Kids)
```bash
python webcheck.py urls.txt
```

**Perfect for:**
- CI/CD pipelines 🔄
- Cron jobs ⏰
- Scripting automation 🤖
- Terminal warriors 💻

### 2️⃣ **Web Interface** (For the Smart Ones)
```bash
python webcheck_web.py
# Open http://localhost:5000
```

**Features:**
- 📁 Drag & drop file upload (so satisfying!)
- ⚡ Real-time progress (watch those green bars!)
- 🎨 Beautiful UI (green theme because we're eco-friendly)
- 💾 Download reports with one click
- 📱 Works on your phone (yes, really)

### 3️⃣ **Google Cloud Shell** (For the Cloud Natives)

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/shadowdevnotreal/URL-Check)

**Why?**
- ✅ Free forever (Google's paying the bill!)
- ✅ Nothing to install locally
- ✅ Works from any browser
- ✅ 5GB persistent storage
- ✅ Your laptop's battery says "thank you"

📖 **[Complete Cloud Shell Guide →](CLOUDSHELL.md)**

---

## 📖 Usage (The Fun Part!)

### Quick Start
```bash
# Basic check
python webcheck.py urls.txt

# With all the bells and whistles
python webcheck.py urls.txt --json --csv --verbose
```

### URL File Format
```
# Group your URLs however you want
Production Sites: Critical Infrastructure
  Full URL: https://api.example.com
  Full URL: https://www.example.com

Staging: Test Before Deploy
  Full URL: https://staging.example.com
```

**Pro Tips:**
- Lines with `:` = group headers
- `Full URL:` prefix = URLs to check
- Missing `http://` or `https://`? We'll add it!
- Malformed URLs? We'll skip 'em with a warning

### Advanced Examples

**Speed demon mode** (use responsibly!):
```bash
python webcheck.py urls.txt --concurrency 100 --rate-limit 0.05
```

**Stealth mode** (avoid rate limits):
```bash
python webcheck.py urls.txt --rate-limit 0.5 --concurrency 10
```

**Error hunting**:
```bash
python webcheck.py urls.txt --error-only --verbose
```

**Config file** (for the organized):
```bash
python webcheck.py urls.txt --config config.yaml
```

**Debug mode** (when things break):
```bash
python webcheck.py urls.txt --verbose --no-ssl-verify
```

---

## ⚙️ Configuration Options

| Option | What It Does | Default | Our Take |
|--------|-------------|---------|----------|
| `--concurrency` | Parallel connections | 30 | Sweet spot for most cases |
| `--retries` | Retry attempts | 3 | Because networks are flaky |
| `--timeout` | HTTP timeout (sec) | 10.0 | Patience has limits |
| `--rate-limit` | Delay between requests (sec) | 0.1 | Play nice with servers |
| `--ssl-verify` | Verify SSL certs | True | Always, unless testing |
| `--error-only` | Show only failures | False | Great for big lists |
| `--verbose` | Debug output | False | When you need details |
| `--json` | Export JSON | False | API-friendly |
| `--csv` | Export CSV | False | Excel-friendly |
| `--html` | Export HTML | True | Human-friendly |

### Config File Example
Create `config.yaml`:
```yaml
concurrency: 30
retries: 3
rate_limit_delay: 0.1
ssl_verify: true
error_only: false
```

Then use it:
```bash
python webcheck.py urls.txt --config config.yaml
```

---

## 🎯 Real-World Use Cases

### 1. Production Monitoring
```bash
# Check every 5 minutes, show only problems
*/5 * * * * python webcheck.py production.txt --error-only --json
```

### 2. Pre-Deployment Validation
```bash
# Verify all endpoints before going live
python webcheck.py staging.txt --concurrency 50 --verbose
```

### 3. Post-Migration Checks
```bash
# After DNS changes, verify everything works
python webcheck.py all-domains.txt --csv --html
```

### 4. SSL Certificate Audit
```bash
# Check SSL on all domains
python webcheck.py domains.txt --verbose --json
```

### 5. Load Testing Prep
```bash
# Verify endpoints can handle traffic
python webcheck.py api-endpoints.txt --concurrency 100
```

---

## 📊 Output Examples

### Console Output (So Pretty!)
```
============================================================
🟢 Google: Search Engine
Original: Full URL: https://www.google.com
Tested:   https://www.google.com
DNS:      142.250.80.46 (0.023s)
TCP:      True (0.145s)
HTTP:     200 (0.312s)
============================================================
```

### HTML Report (Screenshot-Worthy)
Beautiful, responsive reports with:
- 📊 Summary statistics
- 🎨 Color-coded results
- 🔗 Clickable URLs
- ⏱️ Latency charts
- 📱 Mobile-friendly

### JSON Export (For Your Pipeline)
```json
{
  "timestamp": "2025-11-17 12:00:00",
  "total_urls": 50,
  "results": [
    {
      "url": "https://google.com",
      "http_status": 200,
      "dns_latency": 0.023,
      "captcha": false
    }
  ]
}
```

---

## 🔒 Security & Best Practices

### What We Do Right
✅ SSL verification enabled by default
✅ No auto-sudo shenanigans
✅ Comprehensive error handling
✅ Input validation everywhere
✅ No secrets in logs

### How to Use Responsibly
- 🤝 Respect robots.txt
- ⏱️ Use appropriate rate limiting
- 📝 Follow website ToS
- 🔐 Don't bypass CAPTCHAs maliciously
- 🌍 Be a good internet citizen

---

## 🚦 Rate Limiting Guide

### Conservative (Safe Everywhere)
```bash
python webcheck.py urls.txt --rate-limit 0.5 --concurrency 10
```
*Use this for: Checking sites you don't own*

### Moderate (Default)
```bash
python webcheck.py urls.txt --rate-limit 0.1 --concurrency 30
```
*Use this for: Most scenarios*

### Aggressive (YOLO Mode)
```bash
python webcheck.py urls.txt --rate-limit 0.05 --concurrency 100
```
*Use this for: Your own infrastructure only*

**Pro Tip:** Start conservative, increase gradually. Getting blocked isn't fun! 🚫

---

## 🐛 Troubleshooting

### "Import Error: No module named X"
```bash
pip install -r requirements.txt --upgrade
```

### "SSL Certificate Verify Failed"
```bash
# For testing only! Don't do this in production!
python webcheck.py urls.txt --no-ssl-verify
```

### "Too Many Captchas Detected"
```bash
# Slow down!
python webcheck.py urls.txt --rate-limit 1.0 --concurrency 5
```

### "DNS Resolution Failures"
```bash
# Increase timeout
python webcheck.py urls.txt --timeout 30
```

### Still Stuck?
- 📖 Check [Issues](https://github.com/shadowdevnotreal/URL-Check/issues)
- 💬 Start a [Discussion](https://github.com/shadowdevnotreal/URL-Check/discussions)
- ☕ Buy us coffee and we'll help faster 😉

---

## 🛠️ For Developers

### Code Quality
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Modular architecture
- ✅ No spaghetti code (we promise!)

### Want to Contribute?
**We'd love that!** 🎉

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to set up dev environment
- Code style guidelines
- How to submit PRs
- Feature ideas we'd love to see

**Quick Start:**
```bash
# Fork, clone, branch
git clone https://github.com/YOUR-USERNAME/URL-Check
cd URL-Check
git checkout -b feature/my-awesome-idea

# Make changes, test, commit
pytest
black webcheck.py
git commit -m "feat: Add my awesome feature"

# Push and PR
git push origin feature/my-awesome-idea
```

---

## 📈 Performance Benchmarks

| URLs | Concurrency | Time | Avg Latency |
|------|-------------|------|-------------|
| 10   | 10          | ~3s  | 250ms       |
| 50   | 30          | ~8s  | 280ms       |
| 100  | 50          | ~12s | 310ms       |
| 500  | 100         | ~45s | 350ms       |

*Your mileage may vary. Network conditions, server responses, and cosmic radiation may affect results.*

---

## 🎓 Learning Resources

Want to understand the magic under the hood?

- [Python Asyncio Tutorial](https://docs.python.org/3/library/asyncio.html)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)
- [HTTP Status Codes](https://httpstatuses.com/)

---

## 🌟 Hall of Fame

### Contributors
Thanks to these awesome humans! 🙏

- You? (Your name here after first PR!)

### Projects Using WebCheck
- Your project? (Let us know!)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

**TL;DR:** Do whatever you want, just don't sue us. 😅

---

## 🎉 Acknowledgments

Built with love and these amazing tools:
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP magic
- [aiodns](https://github.com/saghul/aiodns) - Async DNS wizardry
- [colorama](https://github.com/tartley/colorama) - Terminal colors
- [tqdm](https://github.com/tqdm/tqdm) - Progress bars
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [PyYAML](https://pyyaml.org/) - Config parsing

Special thanks to:
- Coffee ☕ (the real MVP)
- Stack Overflow 📚 (obviously)
- That one person who actually reads documentation 📖

---

## 💬 Community & Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/shadowdevnotreal/URL-Check/issues)
- 💡 **Feature Requests:** [GitHub Issues](https://github.com/shadowdevnotreal/URL-Check/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/shadowdevnotreal/URL-Check/discussions)
- ☕ **Coffee:** [Buy Me A Coffee](https://www.buymeacoffee.com/diatasso)

---

## 🚀 Roadmap

### Coming Soon™
- [ ] Docker container (because why not?)
- [ ] Prometheus metrics endpoint
- [ ] Webhook notifications (Slack, Discord, etc.)
- [ ] Historical data storage
- [ ] Response time trending
- [ ] API endpoint

### Maybe Someday
- [ ] GUI desktop app
- [ ] Mobile app (iOS/Android)
- [ ] Browser extension
- [ ] AI-powered failure diagnosis
- [ ] World domination 🌍

**Have ideas?** Open an issue! We love feedback!

---

## ⚡ Quick Links

- 📖 [Documentation](README.md) (you are here!)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- ☁️ [Cloud Shell Tutorial](CLOUDSHELL.md)
- 📝 [License](LICENSE)
- 🐛 [Report Bug](https://github.com/shadowdevnotreal/URL-Check/issues)
- ✨ [Request Feature](https://github.com/shadowdevnotreal/URL-Check/issues)
- ⭐ [Star Us](https://github.com/shadowdevnotreal/URL-Check)

---

<p align="center">
  <strong>Made with 💚 for the internet</strong><br>
  <sub>One URL check at a time</sub>
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/diatasso" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 180px !important;" >
  </a>
</p>

<p align="center">
  <sub>If WebCheck saved you time, consider starring ⭐ the repo!</sub>
</p>

---

**Happy URL Checking!** 🎉✨

*P.S. - Yes, we check our own URLs with this tool. Meta, right?* 😎
