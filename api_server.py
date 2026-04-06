from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
from database import Database
from diagnostic_engine import DiagnosticEngine
import json
import os
from datetime import datetime
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = 'bless-auto-diagnostic-secret-key'
CORS(app)

db = Database()
engine = DiagnosticEngine()

# ========== AUTHENTICATION ==========
def hash_password(password):
    salt = secrets.token_hex(16)
    return f"{salt}:{hashlib.sha256((password + salt).encode()).hexdigest()}"

def verify_password(password, stored_hash):
    try:
        salt, hash_value = stored_hash.split(':')
        return hash_value == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, full_name, role FROM users WHERE username = ? AND is_active = 1", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return jsonify({
            'success': True,
            'user': {'id': user[0], 'username': user[1], 'full_name': user[3], 'role': user[4]}
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    return jsonify({'authenticated': True})  # Simplified for now

# ========== DIAGNOSTIC ENDPOINTS ==========
@app.route('/api/diagnose/<diagnostic_type>', methods=['POST'])
def diagnose(diagnostic_type):
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    if diagnostic_type == 'engine':
        result = engine.diagnose_engine(symptoms)
    elif diagnostic_type == 'battery':
        result = engine.diagnose_battery(symptoms)
    elif diagnostic_type == 'starter':
        result = engine.diagnose_starter(symptoms)
    else:
        return jsonify({'error': 'Invalid diagnostic type'}), 400
    
    # Save to database if vehicle_id provided
    if vehicle_id:
        diagnostic_id = db.save_diagnostic(
            vehicle_id=vehicle_id,
            diagnostic_type=diagnostic_type,
            symptoms=symptoms,
            results=result.get('results', ''),
            severity=result.get('severity', 'medium'),
            tools=result.get('tools', []),
            action_plan=result.get('action_plan', [])
        )
        result['diagnostic_id'] = diagnostic_id
    
    return jsonify(result)

# ========== VEHICLE ENDPOINTS ==========
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = db.get_vehicles()
    return jsonify({'vehicles': vehicles})

@app.route('/api/vehicle/add', methods=['POST'])
def add_vehicle():
    data = request.json
    customer_id = data.get('customer_id')
    
    # Create default customer if not exists
    if not customer_id:
        customer_id = db.add_customer(data.get('customer_name', 'Walk-in Customer'))
    
    vehicle_id = db.add_vehicle(
        customer_id=customer_id,
        make=data.get('make'),
        model=data.get('model'),
        year=data.get('year'),
        vin=data.get('vin', ''),
        license_plate=data.get('license_plate', ''),
        mileage=data.get('mileage', 0),
        color=data.get('color', '')
    )
    return jsonify({'success': True, 'vehicle_id': vehicle_id})

@app.route('/api/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = db.get_vehicle(vehicle_id)
    if vehicle:
        return jsonify(vehicle)
    return jsonify({'error': 'Vehicle not found'}), 404

# ========== DIAGNOSTIC HISTORY ==========
@app.route('/api/diagnostics', methods=['GET'])
def get_diagnostics():
    vehicle_id = request.args.get('vehicle_id', type=int)
    diagnostics = db.get_diagnostics(vehicle_id)
    return jsonify({'diagnostics': diagnostics})

# ========== STATISTICS ==========
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = db.get_statistics()
    return jsonify(stats)

# ========== CUSTOMER ENDPOINTS ==========
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = db.get_customers()
    return jsonify({'customers': customers})

@app.route('/api/customer/add', methods=['POST'])
def add_customer():
    data = request.json
    customer_id = db.add_customer(
        name=data.get('name'),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', '')
    )
    return jsonify({'success': True, 'customer_id': customer_id})

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
