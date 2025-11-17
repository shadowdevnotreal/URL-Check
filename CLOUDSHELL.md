# ☁️ Google Cloud Shell Tutorial

Run WebCheck in Google Cloud Shell - a free, browser-based development environment!

## 🚀 Quick Start

### 1. Open in Cloud Shell

Click this button to launch WebCheck in Google Cloud Shell:

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/shadowdevnotreal/URL-Check)

### 2. Install Dependencies

Once Cloud Shell opens, run:

```bash
pip install -r requirements.txt
```

### 3. Run WebCheck

You have two options:

#### Option A: Command Line (CLI)

Create a file with your URLs:

```bash
cat > test-urls.txt << 'EOF'
Google: Search Engine
  Full URL: https://www.google.com
GitHub: Code Hosting
  Full URL: https://github.com
EOF
```

Run the checker:

```bash
python webcheck.py test-urls.txt
```

#### Option B: Web Interface

Start the web server:

```bash
python webcheck_web.py
```

Then click "Web Preview" (🔍) in Cloud Shell toolbar → "Preview on port 5000"

## 📝 Features in Cloud Shell

### ✅ What Works
- ✅ Full CLI functionality
- ✅ Web interface via Web Preview
- ✅ All export formats (HTML, JSON, CSV)
- ✅ File editing with Cloud Shell Editor
- ✅ 5GB persistent storage
- ✅ Free forever (no credit card needed)

### ⚠️ Limitations
- Cloud Shell sessions timeout after 20 minutes of inactivity
- Maximum 50 hours per week of usage
- Web Preview port forwarding required for web interface
- Downloads must use Cloud Shell's download feature

## 🎯 Common Use Cases

### 1. Quick URL Health Check

```bash
# Create URLs file
nano my-urls.txt

# Run check
python webcheck.py my-urls.txt --json --csv

# Download results
cloudshell download webcheck_report.json
```

### 2. Monitor Production Sites

```bash
# Check with error-only mode
python webcheck.py production-sites.txt --error-only --verbose

# View logs
cat webcheck.log
```

### 3. Bulk URL Validation

```bash
# High-speed checking
python webcheck.py bulk-urls.txt --concurrency 50 --rate-limit 0.05 --json
```

## 🔧 Advanced Configuration

### Create Config File

```bash
cat > config.yaml << 'EOF'
concurrency: 30
retries: 3
rate_limit_delay: 0.1
ssl_verify: true
error_only: false
verbose: false
EOF
```

### Run with Config

```bash
python webcheck.py urls.txt --config config.yaml
```

## 💡 Tips & Tricks

### 1. Use Cloud Shell Editor

- Click "Open Editor" to use the built-in file editor
- Edit multiple files at once
- Syntax highlighting and autocomplete

### 2. Download Results

To download files from Cloud Shell:

```bash
# Download HTML report
cloudshell download webcheck_report.html

# Download JSON data
cloudshell download webcheck_report.json
```

### 3. Schedule Checks

Create a simple monitoring script:

```bash
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    python webcheck.py sites.txt --error-only
    sleep 300  # Check every 5 minutes
done
EOF

chmod +x monitor.sh
./monitor.sh
```

### 4. View Results in Browser

For HTML reports:

```bash
python -m http.server 8080
```

Then use Web Preview → Port 8080 to view reports.

## 🌐 Web Interface in Cloud Shell

### Start the Web Server

```bash
python webcheck_web.py
```

### Access the Interface

1. Click "Web Preview" (🔍) in the toolbar
2. Select "Preview on port 5000"
3. A new tab will open with the web interface

### Features

- ✅ Drag-and-drop file upload
- ✅ Real-time progress tracking
- ✅ Interactive result viewing
- ✅ Download reports directly

## 🔒 Security Notes

1. **Files are Private**: Your Cloud Shell home directory is private
2. **HTTPS by Default**: All connections are encrypted
3. **Session Isolation**: Each user gets their own isolated environment
4. **No Local Installation**: Nothing installed on your computer

## 🆘 Troubleshooting

### Port Already in Use

If port 5000 is busy:

```bash
# Use a different port
python -c "from webcheck_web import app; app.run(host='0.0.0.0', port=8080)"
```

### Session Timeout

Cloud Shell sessions timeout after 20 minutes of inactivity. To prevent this:

1. Keep the terminal window active
2. Or use `tmux` to persist sessions:

```bash
# Start tmux session
tmux new -s webcheck

# Run your command
python webcheck_web.py

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t webcheck
```

### Permission Errors

If you get permission errors:

```bash
# Ensure script is executable
chmod +x webcheck.py webcheck_web.py

# Or run with python explicitly
python webcheck.py urls.txt
```

## 📊 Sample Workflow

Here's a complete workflow from start to finish:

```bash
# 1. Clone repo (if not done via button)
git clone https://github.com/shadowdevnotreal/URL-Check
cd URL-Check

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create test URLs
cat > test.txt << 'EOF'
Test Sites:
  Full URL: https://www.google.com
  Full URL: https://github.com
EOF

# 4. Run check
python webcheck.py test.txt --verbose

# 5. View HTML report in browser
python -m http.server 8080
# Then: Web Preview → Port 8080 → Open webcheck_report.html

# 6. Download reports
cloudshell download webcheck_report.json
cloudshell download webcheck_report.csv
```

## 🎓 Learn More

- [Cloud Shell Documentation](https://cloud.google.com/shell/docs)
- [WebCheck GitHub](https://github.com/shadowdevnotreal/URL-Check)
- [Support the Project](https://www.buymeacoffee.com/diatasso)

---

**Happy URL Checking in the Cloud!** ☁️
