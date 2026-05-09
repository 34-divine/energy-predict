const API_URL = 'http://127.0.0.1:5000/api';

async function register() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const message = document.getElementById('message');

    if (!name || !email || !password) {
        message.innerHTML = '<p class="error-msg">All fields are required</p>';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            window.location.href = 'dashboard.html';
        } else {
            message.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        message.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const message = document.getElementById('message');

    if (!email || !password) {
        message.innerHTML = '<p class="error-msg">All fields are required</p>';
        return;
    }

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('name', data.name);
            window.location.href = 'dashboard.html';
        } else {
            message.innerHTML = `<p class="error-msg">${data.error}</p>`;
        }
    } catch (err) {
        message.innerHTML = '<p class="error-msg">Server error. Try again.</p>';
    }
}