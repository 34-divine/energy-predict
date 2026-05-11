const API = 'https://energy-predict-backend.onrender.com/api';

function getToken() {
    return localStorage.getItem('token');
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}

let currentHoursMap = null;
window._suggestions = [];

const USAGE_RANGES = { Light: '0 - 5 hours/day', Average: '5 - 10 hours/day', Heavy: '10 - 24 hours/day' };
const USAGE_MIDPOINTS = { Light: 2.5, Average: 7.5, Heavy: 17 };

window.onload = function () {
    const token = getToken();
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    const name = localStorage.getItem('name');
    if (name) {
        document.getElementById('welcome-name').textContent = 'Hi, ' + name;
    }
    document.getElementById('appliance-usage').addEventListener('change', updateUsageHint);
    loadAppliances();
    loadHistory();
}

// ─── AUTOCOMPLETE ─────────────────────────────────────────────────────────────
async function fetchSuggestions() {
    const query = document.getElementById('appliance-name').value.trim();
    const box = document.getElementById('suggestions-box');

    if (query.length < 1) {
        box.style.display = 'none';
        currentHoursMap = null;
        return;
    }

    try {
        const res = await fetch(`${API}/units/appliances/suggestions?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (data.suggestions.length === 0) {
            box.style.display = 'none';
            currentHoursMap = null;
            return;
        }

        window._suggestions = data.suggestions;

        box.innerHTML = data.suggestions.map((s, index) => `
            <div onmousedown="selectApplianceByIndex(${index})"
                style="padding:10px 14px; cursor:pointer; font-size:14px; border-bottom:1px solid #eee; display:flex; justify-content:space-between; align-items:center;"
                onmouseover="this.style.background='#f0f4f0'"
                onmouseout="this.style.background='white'">
                <span style="font-weight:500;">${s.name}</span>
                <span style="color:#888; font-size:12px;">${s.watts}W</span>
            </div>
        `).join('');

        box.style.display = 'block';
    } catch (err) {
        box.style.display = 'none';
    }
}

function selectApplianceByIndex(index) {
    const s = window._suggestions[index];
    document.getElementById('appliance-name').value = s.name;
    document.getElementById('appliance-watts').value = s.watts;
    document.getElementById('suggestions-box').style.display = 'none';
    currentHoursMap = s.hours;
    updateUsageHint();
}

function hideSuggestions() {
    setTimeout(() => {
        document.getElementById('suggestions-box').style.display = 'none';
    }, 300);
}

function updateUsageHint() {
    const level = document.getElementById('appliance-usage').value;
    const hint = document.getElementById('usage-hint');

    if (!level) {
        hint.textContent = '';
        return;
    }

    hint.textContent = `${level} user (${USAGE_RANGES[level]})`;
}

function getHoursFromLevel(level) {
    return USAGE_MIDPOINTS[level] || 2.5;
}

// ─── ADD APPLIANCE ─────────────────────────────────────────────────────────────
async function addAppliance() {
    const name = document.getElementById('appliance-name').value.trim();
    const watts = document.getElementById('appliance-watts').value;
    const quantity = document.getElementById('appliance-quantity').value || 1;
    const usageLevel = document.getElementById('appliance-usage').value;
    const message = document.getElementById('appliance-message');

    if (!name || !watts || !usageLevel) {
        message.innerHTML = '<p class="error-msg">Appliance name, watts, and usage level are required</p>';
        return;
    }

    const hoursPerDay = getHoursFromLevel(usageLevel);

    try {
        const res = await fetch(`${API}/units/appliances/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getToken()
            },
            body: JSON.stringify({
                name,
                watts: parseFloat(watts),
                hours_per_day: hoursPerDay,
                quantity: parseInt(quantity),
                usage_level: usageLevel
            })
        });
        const data = await res.json();
        if (res.ok) {
            message.innerHTML = `<p class="success-msg">Appliance added. Daily usage: ${data.daily_kwh} kWh</p>`;
            document.getElementById('appliance-name').value = '';
            document.getElementById('appliance-watts').value = '';
            document.getElementById('appliance-quantity').value = '1';
            document.getElementById('appliance-usage').value = '';
            document.getElementById('usage-hint').textContent = '';
            currentHoursMap = null;
            window._suggestions = [];
            loadAppliances();
        } else {
            message.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        message.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}

// ─── LOAD APPLIANCES ──────────────────────────────────────────────────────────
async function loadAppliances() {
    try {
        const res = await fetch(`${API}/units/appliances`, {
            headers: { 'Authorization': 'Bearer ' + getToken() }
        });
        const data = await res.json();
        const list = document.getElementById('appliances-list');
        const total = document.getElementById('total-consumption');

        if (data.appliances.length === 0) {
            list.innerHTML = '<p style="color:#666; font-size:14px;">No appliances added yet.</p>';
            total.textContent = '';
            return;
        }

        list.innerHTML = `
            <table class="log-table">
                <thead>
                    <tr>
                        <th>Appliance</th>
                        <th>Qty</th>
                        <th>Watts</th>
                        <th>Usage</th>
                        <th>Hrs/Day</th>
                        <th>Daily kWh</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.appliances.map(a => `
                        <tr>
                            <td>${a.name}</td>
                            <td>${a.quantity || 1}</td>
                            <td>${a.watts}W</td>
                            <td><span style="background:${a.usage_level === 'Light' ? '#e8f5e9' : a.usage_level === 'Average' ? '#fff3e0' : '#fce4ec'}; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:bold; color:${a.usage_level === 'Light' ? '#1a6b3c' : a.usage_level === 'Average' ? '#e65100' : '#c62828'}">${a.usage_level || 'Custom'}</span></td>
                            <td>${a.hours_per_day} hrs</td>
                            <td>${a.daily_kwh} kWh</td>
                            <td><button onclick="deleteAppliance('${a._id}')" style="background:red; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-size:12px;">Remove</button></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        total.textContent = `Total daily consumption: ${data.total_daily_kwh} kWh`;
    } catch (err) {
        console.error('Error loading appliances:', err);
    }
}

// ─── DELETE APPLIANCE ─────────────────────────────────────────────────────────
async function deleteAppliance(id) {
    try {
        const res = await fetch(`${API}/units/appliances/delete/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + getToken() }
        });
        if (res.ok) {
            loadAppliances();
        }
    } catch (err) {
        console.error('Error deleting appliance:', err);
    }
}

// ─── ADD LOG ──────────────────────────────────────────────────────────────────
async function addLog() {
    const type = document.getElementById('log-type').value;
    const amount = document.getElementById('log-amount').value;
    const note = document.getElementById('log-note').value;
    const message = document.getElementById('log-message');

    if (!amount) {
        message.innerHTML = '<p class="error-msg">Amount is required</p>';
        return;
    }

    try {
        const res = await fetch(`${API}/units/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getToken()
            },
            body: JSON.stringify({ type, amount: parseFloat(amount), note })
        });
        const data = await res.json();
        if (res.ok) {
            message.innerHTML = '<p class="success-msg">Log added successfully</p>';
            document.getElementById('log-amount').value = '';
            document.getElementById('log-note').value = '';
            loadHistory();
        } else {
            message.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        message.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}

// ─── PREDICT ──────────────────────────────────────────────────────────────────
async function predict() {
    const units = document.getElementById('units-bought').value;
    const result = document.getElementById('prediction-result');

    if (!units) {
        result.innerHTML = '<p class="error-msg">Please enter your available units</p>';
        return;
    }

    try {
        const res = await fetch(`${API}/predict/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + getToken()
            },
            body: JSON.stringify({ units_bought: parseFloat(units) })
        });
        const data = await res.json();
        if (res.ok) {
            result.innerHTML = `
                <div class="prediction-result">
                    <div class="value">${data.predicted_days} days</div>
                    <div class="label">${data.message}</div>
                    <div style="margin-top:10px; color:#666; font-size:13px;">Total daily consumption: ${data.total_daily_consumption_kwh} kWh</div>
                </div>`;
        } else {
            result.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        result.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}

// ─── AI ADVICE ────────────────────────────────────────────────────────────────
async function getAIAdvice() {
    const result = document.getElementById('ai-advice-result');
    result.innerHTML = '<p style="color:#1a6b3c;">Analyzing your energy usage, please wait...</p>';

    try {
        const res = await fetch(`${API}/predict/ai-advice`, {
            headers: { 'Authorization': 'Bearer ' + getToken() }
        });
        const data = await res.json();
        if (res.ok) {
            result.innerHTML = `<div style="background:#f9f9f9; padding:15px; border-radius:8px; border-left:4px solid #1a6b3c;">${data.advice.replace(/\n/g, '<br>')}</div>`;
        } else {
            result.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        result.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}

// ─── LOAD HISTORY ─────────────────────────────────────────────────────────────
async function loadHistory() {
    try {
        const res = await fetch(`${API}/units/history`, {
            headers: { 'Authorization': 'Bearer ' + getToken() }
        });
        const data = await res.json();
        const tbody = document.getElementById('log-tbody');

        if (data.logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:20px;">No logs yet</td></tr>';
            return;
        }

        tbody.innerHTML = data.logs.map(log => `
            <tr>
                <td>${log.type === 'bought' ? 'Bought' : 'Finished'}</td>
                <td>${log.amount}</td>
                <td>${log.note || '-'}</td>
                <td>${new Date(log.date).toLocaleString()}</td>
            </tr>
        `).join('');

        renderChart(data.logs);
    } catch (err) {
        console.error('Error loading history:', err);
    }
}

// ─── CHART ────────────────────────────────────────────────────────────────────
function renderChart(logs) {
    const bought = logs.filter(l => l.type === 'bought').reverse();
    const labels = bought.map(l => new Date(l.date).toLocaleDateString());
    const amounts = bought.map(l => l.amount);

    const ctx = document.getElementById('consumptionChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Units Bought (kWh)',
                data: amounts,
                borderColor: '#1a6b3c',
                backgroundColor: 'rgba(26, 107, 60, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } }
        }
    });
}