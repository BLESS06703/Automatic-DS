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
    # Use persistent path for Render
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
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'technician'
        )
    ''')
    
    # Vehicles table
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
    
    # Diagnostics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnostics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            diagnostic_type TEXT,
            symptoms TEXT,
            results TEXT,
            severity TEXT,
            tools TEXT,
            action_plan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', f"{salt}:{hashed}", 'System Administrator', 'admin'))
        print("✅ Admin user created")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize database on startup
init_db()

# Helper function for password verification
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
        return jsonify({
            'success': True,
            'user': {'username': user['username'], 'full_name': user['full_name']}
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': True})

# ========== DIAGNOSTIC ENDPOINTS ==========
@app.route('/api/diagnose/engine', methods=['POST'])
def diagnose_engine():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    results = []
    severity = 'low'
    tools = []
    action_plan = []
    
    if symptoms.get('overheating') == 'yes':
        results.append('Engine overheating detected - Check coolant, radiator, or water pump')
        severity = 'high'
        tools.extend(['Coolant Pressure Tester', 'Infrared Thermometer'])
        action_plan.append('Perform cooling system pressure test')
        action_plan.append('Check coolant level and condition')
    if symptoms.get('smoke') == 'yes':
        results.append('Smoke from exhaust - Possible oil burning or head gasket issue')
        severity = 'high'
        tools.extend(['Compression Tester', 'Leak Down Tester'])
        action_plan.append('Run compression test on all cylinders')
    if symptoms.get('noise') == 'yes':
        results.append('Unusual engine noise - Check belts, pulleys, or internal components')
        severity = 'medium'
        tools.append('Mechanic Stethoscope')
        action_plan.append('Inspect belts and pulleys')
    if symptoms.get('check_light') == 'yes':
        results.append('Check engine light on - OBD2 scan required for error codes')
        severity = 'medium'
        tools.append('OBD2 Scanner')
        action_plan.append('Connect OBD2 scanner and read codes')
    
    if not results:
        results.append('No immediate issues detected. Engine appears healthy')
        action_plan.append('Schedule routine maintenance')
        action_plan.append('Monitor vehicle performance')
    
    # Save to database if vehicle_id provided
    diagnostic_id = None
    if vehicle_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostics (vehicle_id, diagnostic_type, symptoms, results, severity, tools, action_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, 'engine', json.dumps(symptoms), ' '.join(results), severity, json.dumps(tools), json.dumps(action_plan)))
        conn.commit()
        diagnostic_id = cursor.lastrowid
        conn.close()
    
    return jsonify({
        'severity': severity,
        'results': ' '.join(results),
        'symptoms': [k for k, v in symptoms.items() if v == 'yes'],
        'tools': tools,
        'action_plan': action_plan,
        'diagnostic_id': diagnostic_id
    })

@app.route('/api/diagnose/battery', methods=['POST'])
def diagnose_battery():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    results = []
    severity = 'low'
    tools = ['Multimeter', 'Battery Load Tester']
    action_plan = ['Test battery voltage', 'Check alternator output', 'Clean battery terminals']
    
    if symptoms.get('start') == 'yes':
        results.append('Car has trouble starting - Battery may be weak')
        severity = 'medium'
    if symptoms.get('lights') == 'yes':
        results.append('Dim dashboard lights - Charging system issue')
        severity = 'high'
        action_plan.append('Test alternator output (should be 13.7-14.7V)')
    if symptoms.get('clicks') == 'yes':
        results.append('Rapid clicking - Battery charge is very low')
        severity = 'high'
        action_plan.append('Jump start vehicle')
    if symptoms.get('age') == 'yes':
        results.append('Battery over 3 years old - Consider replacement soon')
        action_plan.append('Test battery CCA (Cold Cranking Amps)')
    
    if not results:
        results.append('Battery and charging system appear healthy')
        severity = 'low'
    
    if vehicle_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostics (vehicle_id, diagnostic_type, symptoms, results, severity, tools, action_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, 'battery', json.dumps(symptoms), ' '.join(results), severity, json.dumps(tools), json.dumps(action_plan)))
        conn.commit()
        conn.close()
    
    return jsonify({
        'severity': severity,
        'results': ' '.join(results),
        'symptoms': [k for k, v in symptoms.items() if v == 'yes'],
        'tools': tools,
        'action_plan': action_plan
    })

@app.route('/api/diagnose/starter', methods=['POST'])
def diagnose_starter():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    results = []
    severity = 'low'
    tools = ['Test Light', 'Multimeter', 'Remote Starter Switch']
    action_plan = ['Check battery voltage', 'Test starter relay', 'Inspect starter connections']
    
    if symptoms.get('click') == 'yes' and symptoms.get('crank') == 'no':
        results.append('Clicking but no crank - Weak battery or bad starter')
        severity = 'high'
        action_plan.append('Perform voltage drop test')
    elif symptoms.get('click') == 'no' and symptoms.get('crank') == 'no':
        results.append('No sound, no crank - Ignition switch or wiring issue')
        severity = 'high'
        action_plan.append('Check ignition switch signal')
    if symptoms.get('smell') == 'yes':
        results.append('Burning smell - Starter motor may be failing')
        severity = 'critical'
        action_plan.append('Do not continue cranking - Seek professional help')
    
    if not results:
        results.append('Starter system appears operational')
    
    if vehicle_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostics (vehicle_id, diagnostic_type, symptoms, results, severity, tools, action_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, 'starter', json.dumps(symptoms), ' '.join(results), severity, json.dumps(tools), json.dumps(action_plan)))
        conn.commit()
        conn.close()
    
    return jsonify({
        'severity': severity,
        'results': ' '.join(results),
        'symptoms': [k for k, v in symptoms.items() if v == 'yes'],
        'tools': tools,
        'action_plan': action_plan
    })

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
    conn.execute('''
        INSERT INTO vehicles (make, model, year, license_plate, customer_name)
        VALUES (?, ?, ?, ?, ?)
    ''', (data.get('make'), data.get('model'), data.get('year'), 
          data.get('license_plate', ''), data.get('customer_name', 'Walk-in Customer')))
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

# ========== DIAGNOSTIC HISTORY ==========
@app.route('/api/diagnostics', methods=['GET'])
def get_diagnostics():
    vehicle_id = request.args.get('vehicle_id', type=int)
    conn = get_db()
    if vehicle_id:
        diagnostics = conn.execute('SELECT * FROM diagnostics WHERE vehicle_id = ? ORDER BY created_at DESC', (vehicle_id,)).fetchall()
    else:
        diagnostics = conn.execute('SELECT * FROM diagnostics ORDER BY created_at DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify({'diagnostics': [dict(d) for d in diagnostics]})

# ========== STATISTICS ==========
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db()
    total_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    total_diagnostics = conn.execute('SELECT COUNT(*) FROM diagnostics').fetchone()[0]
    total_customers = conn.execute('SELECT COUNT(DISTINCT customer_name) FROM vehicles').fetchone()[0]
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
