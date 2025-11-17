// WebCheck Web Interface JavaScript

let currentCheckId = null;
let pollInterval = null;

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// Load example URLs
async function loadExample() {
    try {
        const response = await fetch('/api/example');
        const data = await response.json();
        document.getElementById('urls-input').value = data.example;
    } catch (error) {
        console.error('Error loading example:', error);
        alert('Failed to load example');
    }
}

// File upload handling
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');

uploadZone.addEventListener('click', () => {
    fileInput.click();
});

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (!file.name.endsWith('.txt')) {
        alert('Please select a .txt file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('urls-input').value = e.target.result;
        document.getElementById('file-name').textContent = `📄 Loaded: ${file.name}`;

        // Switch to paste tab to show content
        document.getElementById('paste-tab').classList.add('active');
        document.getElementById('upload-tab').classList.remove('active');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.querySelectorAll('.tab-btn')[1].classList.remove('active');
    };
    reader.readAsText(file);
}

// Start check
async function startCheck() {
    const urls = document.getElementById('urls-input').value.trim();

    if (!urls) {
        alert('Please enter some URLs to check');
        return;
    }

    // Get configuration
    const config = {
        urls: urls,
        concurrency: parseInt(document.getElementById('concurrency').value),
        retries: parseInt(document.getElementById('retries').value),
        rate_limit: parseFloat(document.getElementById('rate-limit').value),
        ssl_verify: document.getElementById('ssl-verify').checked,
        error_only: document.getElementById('error-only').checked
    };

    // Disable button
    const checkBtn = document.getElementById('check-btn');
    checkBtn.disabled = true;
    checkBtn.textContent = '⏳ Starting...';

    // Hide results, show progress
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('progress-section').style.display = 'block';

    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        if (data.success) {
            currentCheckId = data.check_id;
            startPolling();
        } else {
            throw new Error(data.error || 'Failed to start check');
        }
    } catch (error) {
        console.error('Error starting check:', error);
        alert('Failed to start check: ' + error.message);
        checkBtn.disabled = false;
        checkBtn.textContent = '🚀 Start Check';
    }
}

// Poll for status updates
function startPolling() {
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${currentCheckId}`);
            const data = await response.json();

            updateProgress(data);

            if (data.status === 'completed') {
                clearInterval(pollInterval);
                showResults(data);
            } else if (data.status === 'error') {
                clearInterval(pollInterval);
                alert('Check failed: ' + data.error);
                resetUI();
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 1000);
}

// Update progress bar
function updateProgress(data) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    const percentage = data.total > 0 ? (data.progress / data.total * 100) : 0;

    progressFill.style.width = percentage + '%';
    progressText.textContent = `Checked ${data.progress} of ${data.total} URLs (${percentage.toFixed(1)}%)`;
}

// Show results
function showResults(data) {
    document.getElementById('progress-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';

    // Show summary
    const summary = data.summary;
    let totalOk = 0, totalWarn = 0, totalFail = 0;

    for (const group in summary) {
        totalOk += summary[group].ok;
        totalWarn += summary[group].warn;
        totalFail += summary[group].fail;
    }

    const total = totalOk + totalWarn + totalFail;

    document.getElementById('summary').innerHTML = `
        <div class="summary-item success">
            <span class="number">${totalOk}</span>
            <span class="label">✅ Success</span>
            <small>${(totalOk/total*100).toFixed(1)}%</small>
        </div>
        <div class="summary-item warning">
            <span class="number">${totalWarn}</span>
            <span class="label">⚠️ Warnings</span>
            <small>${(totalWarn/total*100).toFixed(1)}%</small>
        </div>
        <div class="summary-item error">
            <span class="number">${totalFail}</span>
            <span class="label">❌ Failures</span>
            <small>${(totalFail/total*100).toFixed(1)}%</small>
        </div>
        <div class="summary-item">
            <span class="number">${total}</span>
            <span class="label">📊 Total URLs</span>
        </div>
    `;

    // Show individual results
    const resultsList = document.getElementById('results-list');
    const results = data.results;

    let html = '<h3>Detailed Results</h3>';

    results.forEach(result => {
        const status = getResultStatus(result);
        const icon = getResultIcon(result);

        html += `
            <div class="result-item ${status}">
                <h4>${icon} ${result.group}</h4>
                <div class="detail">
                    <span class="label">URL:</span>
                    <span class="value"><a href="${result.url}" target="_blank">${result.url}</a></span>
                </div>
                <div class="detail">
                    <span class="label">DNS:</span>
                    <span class="value">${result.dns_ip || 'FAILED'} ${formatLatency(result.dns_latency)}</span>
                </div>
                <div class="detail">
                    <span class="label">TCP:</span>
                    <span class="value">${result.tcp_ok !== null ? (result.tcp_ok ? 'OK' : 'FAILED') : 'N/A'} ${formatLatency(result.tcp_latency)}</span>
                </div>
                <div class="detail">
                    <span class="label">HTTP:</span>
                    <span class="value">${result.http_status || 'FAILED'} ${formatLatency(result.http_latency)}</span>
                </div>
                ${result.captcha ? '<div class="detail"><span class="label">⚠️ CAPTCHA DETECTED</span></div>' : ''}
            </div>
        `;
    });

    resultsList.innerHTML = html;

    // Reset button
    resetUI();
}

// Get result status class
function getResultStatus(result) {
    if (result.captcha) return 'warning';
    if (!result.dns_ip || result.tcp_ok === false || (result.http_status && result.http_status >= 400)) {
        return 'error';
    }
    return 'success';
}

// Get result icon
function getResultIcon(result) {
    if (result.captcha) return '🟡';
    if (!result.dns_ip || result.tcp_ok === false || (result.http_status && result.http_status >= 400)) {
        return '🔴';
    }
    return '🟢';
}

// Format latency
function formatLatency(latency) {
    if (latency === null || latency === undefined) return '';
    return `(${(latency * 1000).toFixed(0)}ms)`;
}

// Download report
async function downloadReport(format) {
    if (!currentCheckId) {
        alert('No check completed');
        return;
    }

    try {
        const response = await fetch(`/api/download/${currentCheckId}/${format}`);

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `webcheck_report.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error downloading report:', error);
        alert('Failed to download report');
    }
}

// Reset UI
function resetUI() {
    const checkBtn = document.getElementById('check-btn');
    checkBtn.disabled = false;
    checkBtn.textContent = '🚀 Start Check';
}
