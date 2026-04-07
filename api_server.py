from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = 'bless-auto-diagnostic-secret-key'
CORS(app)

# Database setup
def get_db():
    db_path = '/tmp/workshop.db'
    if not os.environ.get('RENDER'):
        os.makedirs('data', exist_ok=True)
        db_path = 'data/workshop.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'technician'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year INTEGER,
            license_plate TEXT,
            customer_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnostics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            diagnostic_type TEXT,
            results TEXT,
            severity TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)',
                       ('admin', f"{salt}:{hashed}", 'System Administrator', 'admin'))
    
    conn.commit()
    conn.close()
    print("Database initialized")

init_db()

def verify_password(password, stored):
    try:
        salt, hash_val = stored.split(':')
        return hash_val == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False

# ========== AUTHENTICATION ==========
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and verify_password(password, user['password']):
        return jsonify({'success': True, 'user': {'username': user['username'], 'full_name': user['full_name']}})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': True})

# ========== DIAGNOSTIC ENDPOINTS ==========
@app.route('/api/diagnose/engine', methods=['POST'])
def diagnose_engine():
    data = request.json
    symptoms = data.get('symptoms', {})
    results = []
    severity = 'low'
    
    if symptoms.get('overheating') == 'yes':
        results.append('Engine overheating detected')
        severity = 'high'
    if symptoms.get('smoke') == 'yes':
        results.append('Smoke from exhaust detected')
        severity = 'high'
    if not results:
        results.append('No issues detected')
    
    return jsonify({'severity': severity, 'results': ' '.join(results), 'symptoms': [], 'tools': [], 'action_plan': []})

@app.route('/api/diagnose/battery', methods=['POST'])
def diagnose_battery():
    data = request.json
    symptoms = data.get('symptoms', {})
    results = []
    severity = 'low'
    
    if symptoms.get('start') == 'yes':
        results.append('Hard to start')
        severity = 'medium'
    if not results:
        results.append('Battery OK')
    
    return jsonify({'severity': severity, 'results': ' '.join(results), 'symptoms': [], 'tools': [], 'action_plan': []})

@app.route('/api/diagnose/starter', methods=['POST'])
def diagnose_starter():
    data = request.json
    symptoms = data.get('symptoms', {})
    results = []
    severity = 'low'
    
    if symptoms.get('click') == 'yes':
        results.append('Clicking sound detected')
        severity = 'high'
    if not results:
        results.append('Starter OK')
    
    return jsonify({'severity': severity, 'results': ' '.join(results), 'symptoms': [], 'tools': [], 'action_plan': []})

# ========== VEHICLE ENDPOINTS ==========
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = get_db()
    vehicles = conn.execute('SELECT * FROM vehicles ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify({'vehicles': [dict(v) for v in vehicles]})

@app.route('/api/vehicle/add', methods=['POST'])
def add_vehicle():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO vehicles (make, model, year, license_plate, customer_name) VALUES (?, ?, ?, ?, ?)',
                 (data.get('make'), data.get('model'), data.get('year'), data.get('license_plate', ''), data.get('customer_name', 'Walk-in Customer')))
    conn.commit()
    vehicle_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'vehicle_id': vehicle_id})

@app.route('/api/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    conn = get_db()
    conn.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ========== STATISTICS ==========
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db()
    try:
        total_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    except:
        total_vehicles = 0
    try:
        total_diagnostics = conn.execute('SELECT COUNT(*) FROM diagnostics').fetchone()[0]
    except:
        total_diagnostics = 0
    try:
        total_customers = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    except:
        total_customers = 0
    conn.close()
    return jsonify({
        'total_customers': total_customers,
        'total_vehicles': total_vehicles,
        'total_diagnostics': total_diagnostics,
        'total_revenue': total_diagnostics * 5000
    })

# ========== STATIC FILES ==========
@app.route('/')
def home():
    return redirect('/dashboard.html')

@app.route('/dashboard.html')
def serve_dashboard():
    return send_file('dashboard.html')

@app.route('/login.html')
def serve_login():
    return send_file('login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
