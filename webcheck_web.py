#!/usr/bin/env python3
"""
WebCheck Web Interface
Browser-based UI for WebCheck URL health checker
"""

import os
import asyncio
import json
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

# Import webcheck modules
from webcheck import (
    Config, load_urls, check_url, build_summary,
    export_html, export_json, export_csv,
    RateLimiter, setup_logging
)
import aiohttp
import aiodns

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Store active checks
active_checks = {}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
def start_check():
    """Start URL checking process"""
    try:
        # Get configuration from request
        data = request.get_json()

        # Handle file upload or direct URL input
        urls_text = data.get('urls', '')
        concurrency = int(data.get('concurrency', 30))
        retries = int(data.get('retries', 3))
        rate_limit = float(data.get('rate_limit', 0.1))
        error_only = data.get('error_only', False)
        ssl_verify = data.get('ssl_verify', True)

        # Create temp file with URLs
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write(urls_text)
        temp_file.close()

        # Create config
        config = Config(
            concurrency=concurrency,
            retries=retries,
            rate_limit_delay=rate_limit,
            error_only=error_only,
            ssl_verify=ssl_verify
        )

        # Generate check ID
        check_id = f"check_{int(time.time() * 1000)}"

        # Store check info
        active_checks[check_id] = {
            'status': 'running',
            'progress': 0,
            'total': 0,
            'results': [],
            'temp_file': temp_file.name
        }

        # Run check in background
        asyncio.create_task(run_check(check_id, temp_file.name, config))

        return jsonify({'success': True, 'check_id': check_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

async def run_check(check_id, file_path, config):
    """Run URL check asynchronously"""
    try:
        # Load URLs
        entries = load_urls(file_path)
        active_checks[check_id]['total'] = len(entries)

        # Create resolver and rate limiter
        resolver = aiodns.DNSResolver()
        rate_limiter = RateLimiter(config.rate_limit_delay, config.jitter_max)

        # Create HTTP session
        connector = aiohttp.TCPConnector(
            limit=config.concurrency,
            ssl=config.ssl_verify,
            ttl_dns_cache=300,
            force_close=False,
        )

        results = []

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [check_url(e, resolver, session, config, rate_limiter) for e in entries]

            for i, coro in enumerate(asyncio.as_completed(tasks)):
                result = await coro
                results.append(result)

                # Update progress
                active_checks[check_id]['progress'] = i + 1
                active_checks[check_id]['results'].append(result.to_dict())

        # Build summary
        summary = build_summary(results)

        # Generate reports in temp directory
        temp_dir = tempfile.gettempdir()
        report_base = os.path.join(temp_dir, f"webcheck_report_{check_id}")

        export_html(results, summary, f"{report_base}.html")
        export_json(results, f"{report_base}.json")
        export_csv(results, f"{report_base}.csv")

        # Update status
        active_checks[check_id]['status'] = 'completed'
        active_checks[check_id]['summary'] = summary
        active_checks[check_id]['report_path'] = report_base

        # Cleanup temp URL file
        try:
            os.unlink(file_path)
        except:
            pass

    except Exception as e:
        active_checks[check_id]['status'] = 'error'
        active_checks[check_id]['error'] = str(e)

@app.route('/api/status/<check_id>')
def check_status(check_id):
    """Get status of a check"""
    if check_id not in active_checks:
        return jsonify({'error': 'Check not found'}), 404

    check = active_checks[check_id]

    return jsonify({
        'status': check['status'],
        'progress': check['progress'],
        'total': check['total'],
        'results': check.get('results', []),
        'summary': check.get('summary', {}),
        'error': check.get('error', None)
    })

@app.route('/api/download/<check_id>/<format>')
def download_report(check_id, format):
    """Download report in specified format"""
    if check_id not in active_checks:
        return jsonify({'error': 'Check not found'}), 404

    check = active_checks[check_id]

    if check['status'] != 'completed':
        return jsonify({'error': 'Check not completed'}), 400

    report_base = check['report_path']

    if format == 'html':
        file_path = f"{report_base}.html"
        mimetype = 'text/html'
    elif format == 'json':
        file_path = f"{report_base}.json"
        mimetype = 'application/json'
    elif format == 'csv':
        file_path = f"{report_base}.csv"
        mimetype = 'text/csv'
    else:
        return jsonify({'error': 'Invalid format'}), 400

    if not os.path.exists(file_path):
        return jsonify({'error': 'Report file not found'}), 404

    return send_file(file_path, mimetype=mimetype, as_attachment=True,
                     download_name=f"webcheck_report.{format}")

@app.route('/api/example')
def get_example():
    """Get example URL format"""
    example = """AK (Alaska): www.commerce.alaska.gov
  Full URL: https://www.commerce.alaska.gov/cbp/main/Search/Professional
AL (Alabama): www.albme.org
  Full URL: https://www.albme.org/Licensing/Verification.aspx
AR (Arkansas): www.armedicalboard.org
  Full URL: https://www.armedicalboard.org/Public/verify/default.aspx"""

    return jsonify({'example': example})

def main():
    """Run the web application"""
    # Header with emoji-aware width (emojis take 2 columns)
    print("\n" + "=" * 50)
    print("  🌐 WebCheck Web Interface")
    print("=" * 50)
    print("\n  🚀 Starting server on http://localhost:5000")
    print("  💡 Press Ctrl+C to stop\n")

    # Get event loop for async tasks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
