// ========== Global Variables ==========
const API_BASE = window.location.origin;
let diagnosticHistory = [];
let currentDiagnosticType = 'engine';
let currentUser = null;

// ========== Authentication ==========
async function checkAuth() {
    try {
        const res = await fetch(`${API_BASE}/api/check-auth`);
        const data = await res.json();
        if (!data.authenticated) {
            window.location.href = '/login.html';
        } else {
            currentUser = data.user;
            document.getElementById('userName').innerHTML = data.user?.full_name || 'Technician';
            loadStats();
            loadQuestions();
        }
    } catch(e) {
        window.location.href = '/login.html';
    }
}

async function logout() {
    await fetch(`${API_BASE}/api/logout`, { method: 'POST' });
    window.location.href = '/login.html';
}

// ========== UI Navigation ==========
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
    document.getElementById(`${tabName}Tab`).classList.remove('hidden');
    
    // Update sidebar active state
    document.querySelectorAll('.sidebar-item').forEach(item => item.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update page title
    const titles = {
        diagnostic: { title: 'Diagnostic Machine', subtitle: 'Run real-time vehicle diagnostics' },
        scanner: { title: 'Car Scanner Tools', subtitle: 'OBD2 scanner interface' },
        history: { title: 'Diagnostic History', subtitle: 'View past diagnostic logs' },
        analytics: { title: 'Industrial Analytics', subtitle: 'Performance metrics and insights' },
        settings: { title: 'Settings', subtitle: 'Customize your dashboard' }
    };
    document.getElementById('pageTitle').innerHTML = titles[tabName].title;
    document.getElementById('pageSubtitle').innerHTML = titles[tabName].subtitle;
    
    if (tabName === 'history') loadHistory();
}

// ========== Dynamic Questions ==========
function loadQuestions() {
    const questionsMap = {
        engine: `
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Engine overheating?</label>
            <select id="engine_overheating" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Smoke from exhaust?</label>
            <select id="engine_smoke" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Unusual engine noise?</label>
            <select id="engine_noise" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Check engine light ON?</label>
            <select id="engine_check_light" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
        `,
        battery: `
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Car fails to start?</label>
            <select id="battery_start" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Dashboard lights dim?</label>
            <select id="battery_lights" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Rapid clicking sound?</label>
            <select id="battery_clicks" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Battery over 3 years old?</label>
            <select id="battery_age" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
        `,
        starter: `
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Clicking when turning key?</label>
            <select id="starter_click" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Engine cranks at all?</label>
            <select id="starter_crank" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Headlights work?</label>
            <select id="starter_lights" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="yes">Yes</option><option value="no">No</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-2">Burning smell?</label>
            <select id="starter_smell" class="w-full border border-gray-300 rounded-lg px-4 py-2"><option value="no">No</option><option value="yes">Yes</option></select></div>
        `
    };
    
    document.getElementById('dynamicQuestions').innerHTML = questionsMap[currentDiagnosticType] || questionsMap.engine;
    
    // Add event listener for system select
    document.getElementById('systemSelect').addEventListener('change', (e) => {
        currentDiagnosticType = e.target.value;
        document.getElementById('dynamicQuestions').innerHTML = questionsMap[currentDiagnosticType];
    });
}

// ========== Run Diagnostic ==========
async function runDiagnostic() {
    const symptoms = {};
    const prefix = currentDiagnosticType + '_';
    document.querySelectorAll(`[id^="${prefix}"]`).forEach(el => {
        symptoms[el.id.replace(prefix, '')] = el.value;
    });
    
    // Show loading state
    const resultsArea = document.getElementById('resultsArea');
    resultsArea.innerHTML = '<div class="text-center py-12"><div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-[#003153]"></div><p class="mt-4">Running diagnostic...</p></div>';
    
    try {
        const res = await fetch(`${API_BASE}/api/diagnose/${currentDiagnosticType}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symptoms })
        });
        const result = await res.json();
        
        displayResults(result);
        
        // Save to history
        diagnosticHistory.unshift({
            id: Date.now(),
            type: currentDiagnosticType,
            date: new Date().toLocaleString(),
            severity: result.severity,
            results: result.results
        });
        localStorage.setItem('diagnosticHistory', JSON.stringify(diagnosticHistory));
        
    } catch(e) {
        resultsArea.innerHTML = '<div class="text-center py-12 text-red-500"><span class="mdi mdi-alert-circle text-4xl"></span><p>Error running diagnostic</p></div>';
    }
}

function displayResults(result) {
    const severityColors = {
        low: 'bg-green-100 text-green-800',
        medium: 'bg-yellow-100 text-yellow-800',
        high: 'bg-red-100 text-red-800',
        critical: 'bg-purple-100 text-purple-800'
    };
    
    let toolsHtml = result.tools?.length ? `
        <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <strong class="block mb-2">🛠️ Tools Required</strong>
            <ul class="list-disc list-inside space-y-1">${result.tools.map(t => `<li>${t}</li>`).join('')}</ul>
        </div>
    ` : '';
    
    let actionHtml = result.action_plan?.length ? `
        <div class="mt-4 p-4 bg-gray-50 rounded-lg">
            <strong class="block mb-2">📋 Action Plan</strong>
            <ol class="list-decimal list-inside space-y-1">${result.action_plan.map(s => `<li>${s}</li>`).join('')}</ol>
        </div>
    ` : '';
    
    document.getElementById('resultsArea').innerHTML = `
        <div class="space-y-4">
            <div class="p-4 rounded-lg ${severityColors[result.severity] || 'bg-gray-100'}">
                <strong>⚠️ Severity:</strong> ${result.severity?.toUpperCase() || 'MEDIUM'}
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
                <strong class="block mb-2">🔍 Symptoms Found</strong>
                <ul class="list-disc list-inside">${result.symptoms?.map(s => `<li>${s}</li>`).join('') || '<li>No symptoms recorded</li>'}</ul>
            </div>
            <div class="p-4 bg-gray-50 rounded-lg">
                <strong class="block mb-2">📊 Analysis</strong>
                <p>${result.results || 'No issues found'}</p>
            </div>
            ${toolsHtml}
            ${actionHtml}
            <div class="flex gap-2 pt-4">
                <button onclick="generateReport()" class="flex-1 px-4 py-2 bg-[#003153] text-white rounded-lg hover:bg-[#1B4F72]">📄 Generate Report</button>
                <button onclick="shareDiagnostic()" class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">📧 Share</button>
            </div>
        </div>
    `;
}

// ========== History ==========
function loadHistory() {
    const saved = localStorage.getItem('diagnosticHistory');
    if (saved) diagnosticHistory = JSON.parse(saved);
    
    const historyDiv = document.getElementById('historyLogs');
    if (diagnosticHistory.length === 0) {
        historyDiv.innerHTML = '<div class="text-center text-gray-400 py-8">No diagnostic history yet. Run a diagnosis to see logs.</div>';
        return;
    }
    
    historyDiv.innerHTML = diagnosticHistory.map(log => `
        <div class="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div class="flex justify-between items-start mb-2">
                <span class="font-semibold">${log.type.toUpperCase()} Diagnostic</span>
                <span class="text-xs text-gray-500">${log.date}</span>
            </div>
            <div class="text-sm text-gray-600">${log.results.substring(0, 100)}...</div>
            <div class="mt-2"><span class="inline-block px-2 py-1 text-xs rounded ${log.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}">${log.severity}</span></div>
        </div>
    `).join('');
}

// ========== Stats ==========
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/statistics`);
        const stats = await res.json();
        // Update sidebar stats if needed
    } catch(e) {}
}

// ========== Dark Mode ==========
function toggleDarkMode() {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('darkMode', isDark);
    
    if (isDark) {
        document.body.classList.add('bg-gray-900');
        document.querySelectorAll('.bg-white').forEach(el => el.classList.add('bg-gray-800', 'border-gray-700'));
        document.getElementById('themeIcon').className = 'mdi mdi-white-balance-sunny text-xl text-gray-400';
    } else {
        document.body.classList.remove('bg-gray-900');
        document.querySelectorAll('.bg-white').forEach(el => el.classList.remove('bg-gray-800', 'border-gray-700'));
        document.getElementById('themeIcon').className = 'mdi mdi-weather-night text-xl text-gray-600';
    }
}

// ========== Helper Functions ==========
function generateReport() {
    alert('📄 Report generation will be available in the next update');
}

function shareDiagnostic() {
    alert('📧 Share feature coming soon');
}

// ========== Initialize ==========
checkAuth();
loadQuestions();
