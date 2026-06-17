// ============================================================
// JobPilot AI — Dashboard Logic
// ============================================================

const API = '';
let eventSource = null;
let botRunning = false;
let statsPoller = null;

// --- DOM Elements ---
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const statusBadge = $('#statusBadge');
const statusText = $('#statusText');
const startBtn = $('#startBtn');
const stopBtn = $('#stopBtn');
const feedContainer = $('#feedContainer');
const feedEmpty = $('#feedEmpty');
const dropZone = $('#dropZone');
const fileInput = $('#fileInput');
const resumeList = $('#resumeList');
const resumeParsed = $('#resumeParsed');
const toastContainer = $('#toastContainer');

// Stat values
const valJobsFound = $('#valJobsFound');
const valApplied = $('#valApplied');
const valSkipped = $('#valSkipped');
const valFailed = $('#valFailed');

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    loadResumes();
    loadConfig();
    checkBotStatus(); // Reconnect if bot already running

    // Platform toggle visibility
    $('[name="platform_linkedin"]').addEventListener('change', (e) => {
        $('#linkedinCreds').style.display = e.target.checked ? 'block' : 'none';
    });
    $('[name="platform_naukri"]').addEventListener('change', (e) => {
        $('#naukriCreds').style.display = e.target.checked ? 'block' : 'none';
    });

    // Drop zone
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault(); dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', (e) => { if (e.target.files.length) uploadFile(e.target.files[0]); });

    // Buttons
    startBtn.addEventListener('click', startBot);
    stopBtn.addEventListener('click', stopBot);
    $('#clearLogs').addEventListener('click', clearLogs);
    $('#refreshResumes').addEventListener('click', loadResumes);
    $('#settingsBtn').addEventListener('click', () => {
        $('#configCard').scrollIntoView({ behavior: 'smooth' });
    });
    $('#clearAllAnswers').addEventListener('click', clearAllAnswers);
    loadSavedAnswers();

    // Sign-in buttons
    $('#signinLinkedin').addEventListener('click', () => signinRedirect('linkedin'));
    $('#signinNaukri').addEventListener('click', () => signinRedirect('naukri'));
});

// --- API Calls ---
async function apiGet(path) {
    const r = await fetch(API + path);
    return r.json();
}
async function apiPost(path, body = {}) {
    const r = await fetch(API + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    return r.json();
}

// --- Resume Management (single resume at a time) ---
async function loadResumes() {
    try {
        const resumes = await apiGet('/api/resumes');
        resumeList.innerHTML = '';
        resumeParsed.style.display = 'none';

        if (resumes.length > 0) {
            // Hide drop zone when resume exists
            dropZone.style.display = 'none';
            const r = resumes[0]; // Only show first/only resume
            const div = document.createElement('div');
            div.className = 'resume-item active';
            div.innerHTML = `
                <div class="resume-item-icon">${r.type}</div>
                <div class="resume-item-info">
                    <div class="resume-item-name">${r.name}</div>
                    <div class="resume-item-size">${formatSize(r.size)}</div>
                </div>
                <button class="resume-item-parse" data-name="${r.name}">Parse AI</button>
                <button class="resume-item-delete" data-name="${r.name}" title="Remove resume">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                </button>
            `;
            div.querySelector('.resume-item-parse').addEventListener('click', (e) => {
                e.stopPropagation();
                parseResume(r.name);
            });
            div.querySelector('.resume-item-delete').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteResume(r.name);
            });
            resumeList.appendChild(div);
        } else {
            // Show drop zone when no resume
            dropZone.style.display = 'flex';
        }
    } catch (e) {
        console.error('Load resumes error:', e);
    }
}

async function uploadFile(file) {
    const fd = new FormData();
    fd.append('file', file);
    try {
        const r = await fetch(API + '/api/upload-resume', { method: 'POST', body: fd });
        const data = await r.json();
        if (data.error) { toast(data.error, 'error'); return; }
        toast(`Resume uploaded: ${data.name}`, 'success');
        await loadResumes();
        // Auto-parse after upload
        parseResume(data.name);
    } catch (e) {
        toast('Upload failed', 'error');
    }
}

async function deleteResume(filename) {
    try {
        const data = await apiPost('/api/delete-resume', { filename });
        if (data.error) { toast(data.error, 'error'); return; }
        toast('Resume removed', 'success');
        resumeParsed.style.display = 'none';
        $('#keywords').value = '';
        loadResumes();
    } catch (e) {
        toast('Delete failed', 'error');
    }
}

async function parseResume(filename) {
    toast('Parsing resume with AI...', 'info');
    try {
        const data = await apiPost('/api/parse-resume', { filename });
        if (data.error) { toast(data.error, 'error'); return; }
        showParsedResume(data);
        // Auto-fill keywords
        if (data.search_keywords && data.search_keywords.length) {
            $('#keywords').value = data.search_keywords.join(', ');
        }
        toast('Resume parsed!', 'success');
    } catch (e) {
        toast('Parse failed', 'error');
    }
}

function showParsedResume(data) {
    resumeParsed.style.display = 'block';
    $('#parsedName').textContent = data.name || 'Candidate';
    const skillsDiv = $('#parsedSkills');
    const kwDiv = $('#parsedKeywords');

    // Show contact info that will be used for form filling
    let contactHtml = '<span style="font-size:0.7rem;color:var(--text-muted);width:100%;margin-bottom:4px">Contact Info (auto-fill):</span>';
    if (data.phone) contactHtml += `<span class="tag" style="background:rgba(16,185,129,0.1);color:var(--accent-green);border-color:rgba(16,185,129,0.2)">📱 ${data.phone}</span>`;
    if (data.email) contactHtml += `<span class="tag" style="background:rgba(16,185,129,0.1);color:var(--accent-green);border-color:rgba(16,185,129,0.2)">✉️ ${data.email}</span>`;
    if (data.current_location) contactHtml += `<span class="tag" style="background:rgba(16,185,129,0.1);color:var(--accent-green);border-color:rgba(16,185,129,0.2)">📍 ${data.current_location}</span>`;

    skillsDiv.innerHTML = contactHtml;

    kwDiv.innerHTML = '<span style="font-size:0.7rem;color:var(--text-muted);width:100%;margin-bottom:4px">Skills:</span>';
    (data.skills || []).forEach((s) => {
        kwDiv.innerHTML += `<span class="tag">${s}</span>`;
    });

    // Add search keywords below
    if (data.search_keywords && data.search_keywords.length) {
        kwDiv.innerHTML += '<span style="font-size:0.7rem;color:var(--text-muted);width:100%;margin-bottom:4px;margin-top:8px">Search Keywords:</span>';
        data.search_keywords.forEach((k) => {
            kwDiv.innerHTML += `<span class="tag" style="background:rgba(124,58,237,0.1);color:var(--accent-violet);border-color:rgba(124,58,237,0.2)">${k}</span>`;
        });
    }
}

// --- Config ---
async function loadConfig() {
    try {
        const cfg = await apiGet('/api/config');
        if (cfg.linkedin_email) $('#linkedinEmail').value = cfg.linkedin_email;
        if (cfg.naukri_email) $('#naukriEmail').value = cfg.naukri_email;
        if (cfg.keywords && cfg.keywords.length) $('#keywords').value = cfg.keywords.join(', ');
        if (cfg.location && cfg.location.length) $('#location').value = cfg.location[0];
        if (cfg.experience_levels && cfg.experience_levels.length) $('#experience').value = cfg.experience_levels[0];
        if (cfg.date_posted) $('#datePosted').value = cfg.date_posted;
        if (cfg.max_applications) $('#maxApps').value = cfg.max_applications;
        if (cfg.dry_run) $('#dryRun').value = 'true';
    } catch (e) {
        console.error('Config load error:', e);
    }
}

function getConfigFromForm() {
    const platforms = [];
    if ($('[name="platform_linkedin"]').checked) platforms.push('linkedin');
    if ($('[name="platform_naukri"]').checked) platforms.push('naukri');

    const kwRaw = $('#keywords').value.trim();
    const keywords = kwRaw ? kwRaw.split(',').map(s => s.trim()).filter(Boolean) : [];

    const blRaw = $('#blacklistCompanies').value.trim();
    const blacklist = blRaw ? blRaw.split(',').map(s => s.trim()).filter(Boolean) : [];

    return {
        platforms,
        linkedin_email: $('#linkedinEmail').value.trim(),
        linkedin_password: $('#linkedinPass').value,
        naukri_email: $('#naukriEmail').value.trim(),
        naukri_password: $('#naukriPass').value,

        keywords,
        location: [$('#location').value.trim() || 'India'],
        experience_levels: [$('#experience').value],
        date_posted: $('#datePosted').value,
        max_applications: parseInt($('#maxApps').value) || 50,
        dry_run: $('#dryRun').value === 'true',
        blacklist_companies: blacklist,
    };
}

// --- Bot Control ---
async function startBot() {
    const config = getConfigFromForm();
    if (!config.platforms.length) { toast('Select at least one platform', 'error'); return; }
    if (config.platforms.includes('linkedin') && !config.linkedin_email) { toast('Enter LinkedIn email', 'error'); return; }
    if (config.platforms.includes('linkedin') && !config.linkedin_password) { toast('Enter LinkedIn password', 'error'); return; }
    if (config.platforms.includes('naukri') && !config.naukri_email) { toast('Enter Naukri email', 'error'); return; }
    if (config.platforms.includes('naukri') && !config.naukri_password) { toast('Enter Naukri password', 'error'); return; }

    // Save config first
    await apiPost('/api/config', config);

    // Start
    startBtn.style.display = 'none';
    stopBtn.style.display = 'flex';
    $('#signinSection').style.display = 'none';
    setStatus('running', 'Starting...');

    try {
        const result = await apiPost('/api/start', config);
        if (result.error) {
            toast(result.error, 'error');
            resetUI();
            return;
        }
        botRunning = true;
        connectSSE();
        startStatsPolling();
        toast('Bot started!', 'success');
    } catch (e) {
        toast('Start failed', 'error');
        resetUI();
    }
}

async function stopBot() {
    try {
        await apiPost('/api/stop');
        toast('Stop signal sent', 'info');
        setStatus('idle', 'Stopping...');
    } catch (e) {
        toast('Stop failed', 'error');
    }
}

function resetUI() {
    startBtn.style.display = 'flex';
    stopBtn.style.display = 'none';
    $('#signinSection').style.display = 'block';
    setStatus('idle', 'Idle');
    botRunning = false;
    stopStatsPolling();
}

function setStatus(state, text) {
    statusBadge.className = 'status-badge ' + state;
    statusText.textContent = text;
}

// --- Auto-reconnect if bot running on page load ---
async function checkBotStatus() {
    try {
        const data = await apiGet('/api/status');
        if (data.status === 'running' || data.status === 'signing_in') {
            botRunning = true;
            startBtn.style.display = 'none';
            stopBtn.style.display = 'flex';
            $('#signinSection').style.display = 'none';
            setStatus('running', data.status === 'signing_in' ? 'Signing in...' : 'Running...');
            connectSSE();
            startStatsPolling();
            // Load existing log history
            const history = await apiGet('/api/log-history');
            if (history && history.length) {
                history.forEach(evt => {
                    if (evt.type === 'stats') updateStats(evt.data);
                    else if (evt.type !== 'heartbeat') addFeedItem(evt);
                });
            }
            if (data.stats) updateStats(data.stats);
            toast('Reconnected to running bot', 'info');
        }
    } catch (e) { /* server not running yet */ }
}

// --- Stats Polling (fallback for missed SSE) ---
function startStatsPolling() {
    stopStatsPolling();
    statsPoller = setInterval(async () => {
        try {
            const data = await apiGet('/api/stats');
            if (data) updateStats(data);
            const status = await apiGet('/api/status');
            if (status.status === 'running' && !botRunning) {
                // Transitioned from signing_in to running
                botRunning = true;
                setStatus('running', 'Running...');
            }
            if (status.status === 'signing_in') {
                setStatus('running', 'Waiting for sign-in...');
            }
            if (status.status === 'idle' && botRunning) {
                resetUI();
                toast('Bot finished!', 'success');
            }
        } catch (e) {}
    }, 5000);
}

function stopStatsPolling() {
    if (statsPoller) { clearInterval(statsPoller); statsPoller = null; }
}

// --- SSE ---
function connectSSE() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource(API + '/api/logs');

    eventSource.onmessage = (e) => {
        try {
            const event = JSON.parse(e.data);
            if (event.type === 'heartbeat') return;
            if (event.type === 'stats') {
                updateStats(event.data);
                return;
            }
            if (event.type === 'question') {
                addQuestionPrompt(event);
                return;
            }
            addFeedItem(event);
            if (event.type === 'complete') {
                updateStats(event.data);
                resetUI();
                hideQuestionPrompt();
                if (eventSource) eventSource.close();
            }
        } catch (err) {
            console.error('SSE parse error:', err);
        }
    };

    eventSource.onerror = () => {
        console.warn('SSE connection lost, reconnecting...');
        setTimeout(() => {
            if (botRunning) connectSSE();
        }, 3000);
    };
}

// --- Feed ---
function addFeedItem(event) {
    if (feedEmpty) feedEmpty.style.display = 'none';
    const div = document.createElement('div');
    div.className = `feed-item ${event.type}`;
    div.innerHTML = `
        <span class="feed-time">${event.timestamp}</span>
        <span class="feed-msg">${escapeHtml(event.message)}</span>
    `;
    feedContainer.appendChild(div);
    feedContainer.scrollTop = feedContainer.scrollHeight;

    // Keep max 200 items
    while (feedContainer.children.length > 201) {
        feedContainer.removeChild(feedContainer.children[1]);
    }
}

function clearLogs() {
    feedContainer.innerHTML = '';
    feedContainer.appendChild(feedEmpty);
    feedEmpty.style.display = 'flex';
}

// --- Stats ---
function updateStats(data) {
    if (!data) return;
    animateValue(valJobsFound, data.jobs_found || 0);
    animateValue(valApplied, data.applied || 0);
    animateValue(valSkipped, (data.blacklisted || 0) + (data.already_applied || 0) + (data.skipped || 0));
    animateValue(valFailed, data.failed || 0);
}

function animateValue(el, target) {
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    el.textContent = target;
    el.style.transform = 'scale(1.2)';
    el.style.color = 'var(--accent-cyan)';
    setTimeout(() => {
        el.style.transform = 'scale(1)';
        el.style.color = '';
    }, 300);
}

// --- Toast ---
function toast(message, type = 'info') {
    const div = document.createElement('div');
    div.className = `toast ${type}`;
    div.textContent = message;
    toastContainer.appendChild(div);
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transform = 'translateY(20px)';
        setTimeout(() => div.remove(), 300);
    }, 4000);
}

// --- Utils ---
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// --- Interactive Question Prompt ---
function addQuestionPrompt(event) {
    // Add the question as a feed item first
    addFeedItem(event);

    // Remove any existing prompt
    hideQuestionPrompt();

    // Create interactive prompt
    const prompt = document.createElement('div');
    prompt.className = 'question-prompt';
    prompt.id = 'questionPrompt';
    prompt.innerHTML = `
        <div class="question-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span>Bot needs your input</span>
        </div>
        <div class="question-field">${escapeHtml(event.data.field || '')}</div>
        <div class="question-input-row">
            <input type="text" class="question-input" id="questionInput" placeholder="Type your answer..." autofocus>
            <button class="btn btn-primary btn-sm" id="questionSendBtn">Send</button>
            <button class="btn btn-ghost btn-sm" id="questionSkipBtn">Skip</button>
        </div>
    `;

    feedContainer.appendChild(prompt);
    feedContainer.scrollTop = feedContainer.scrollHeight;

    // Focus the input
    const input = prompt.querySelector('#questionInput');
    setTimeout(() => input.focus(), 100);

    // Send on Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && input.value.trim()) {
            submitAnswer(input.value.trim());
        }
    });

    // Send button
    prompt.querySelector('#questionSendBtn').addEventListener('click', () => {
        if (input.value.trim()) submitAnswer(input.value.trim());
    });

    // Skip button
    prompt.querySelector('#questionSkipBtn').addEventListener('click', () => {
        submitAnswer('__SKIP__');
    });

    // Play notification sound (optional visual pulse)
    setStatus('running', '⏸ Waiting for input...');
    toast('Bot needs your input!', 'info');
}

function hideQuestionPrompt() {
    const existing = document.getElementById('questionPrompt');
    if (existing) existing.remove();
}

async function submitAnswer(answer) {
    hideQuestionPrompt();
    if (answer === '__SKIP__') {
        addFeedItem({ type: 'warning', message: '⏭️ Skipped field', timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }) });
    } else {
        addFeedItem({ type: 'info', message: `📤 Sent: "${answer}"`, timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }) });
    }
    setStatus('running', 'Running...');
    try {
        await apiPost('/api/respond', { answer });
        // Reload saved answers after new answer is submitted
        setTimeout(loadSavedAnswers, 1000);
    } catch (e) {
        toast('Failed to send answer', 'error');
    }
}

// --- Saved Answers Management ---
async function loadSavedAnswers() {
    try {
        const data = await apiGet('/api/saved-answers');
        const list = $('#savedAnswersList');
        const empty = $('#savedAnswersEmpty');
        const keys = Object.keys(data);
        list.innerHTML = '';
        if (keys.length === 0) {
            list.appendChild(createEmptyAnswersDiv());
            return;
        }
        keys.forEach(key => {
            const item = document.createElement('div');
            item.className = 'saved-answer-item';
            item.innerHTML = `
                <div class="saved-answer-q">❓ ${escapeHtml(key)}</div>
                <div class="saved-answer-a">💬 ${escapeHtml(data[key])}</div>
                <button class="saved-answer-del" data-key="${escapeHtml(key)}" title="Delete this answer">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
            `;
            item.querySelector('.saved-answer-del').addEventListener('click', async (e) => {
                e.stopPropagation();
                const k = e.currentTarget.dataset.key;
                await apiPost('/api/delete-answer', { key: k });
                toast(`Deleted: ${k}`, 'info');
                loadSavedAnswers();
            });
            list.appendChild(item);
        });
    } catch (e) {
        console.error('Load saved answers error:', e);
    }
}

function createEmptyAnswersDiv() {
    const div = document.createElement('div');
    div.className = 'saved-answers-empty';
    div.id = 'savedAnswersEmpty';
    div.innerHTML = '<p>No saved answers yet</p><p class="drop-sub">Bot will learn from your inputs</p>';
    return div;
}

async function clearAllAnswers() {
    if (!confirm('Clear ALL saved answers? Bot will ask everything again.')) return;
    try {
        await fetch(API + '/api/saved-answers', { method: 'DELETE' });
        toast('All saved answers cleared', 'success');
        loadSavedAnswers();
    } catch (e) {
        toast('Clear failed', 'error');
    }
}

// --- Sign-In Redirect Flow ---
async function signinRedirect(platform) {
    const config = getConfigFromForm();
    // Save config
    await apiPost('/api/config', config);

    // Disable buttons, show signing in
    startBtn.style.display = 'none';
    stopBtn.style.display = 'flex';
    $('#signinSection').style.display = 'none';
    setStatus('running', `Signing in to ${platform}...`);

    try {
        const result = await apiPost('/api/signin', { platform, ...config });
        if (result.error) {
            toast(result.error, 'error');
            resetUI();
            return;
        }
        botRunning = true;
        connectSSE();
        startStatsPolling();
        toast(`${platform} sign-in page opened!`, 'success');
    } catch (e) {
        toast('Sign-in failed', 'error');
        resetUI();
    }
}
