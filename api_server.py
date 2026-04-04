from flask import Flask, request, jsonify, send_file, redirect, session
from flask_cors import CORS
from database import Database
from diagnostic_engine import DiagnosticEngine
from report_generator import ReportGenerator
from config import Config
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'bless-auto-diagnostic-secret-key'
CORS(app)

db = Database()
engine = DiagnosticEngine()

# ========== SIMPLE AUTHENTICATION (NO DATABASE NEEDED) ==========
# Hardcoded admin user for testing
USERS = {
    'admin': hashlib.sha256('admin123'.encode()).hexdigest()
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username] == hashlib.sha256(password.encode()).hexdigest():
        session['user'] = username
        return jsonify({'success': True, 'message': 'Login successful', 'user': {'username': username, 'role': 'admin'}})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'success': True})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if session.get('user'):
        return jsonify({'authenticated': True, 'user': {'username': session['user']}})
    return jsonify({'authenticated': False})

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            return jsonify({'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated

# ========== WEB ROUTES ==========
@app.route('/')
def home():
    return redirect('/login.html')

@app.route('/login.html')
def serve_login():
    return send_file('login.html')

@app.route('/web_interface.html')
def serve_app():
    return send_file('web_interface.html')

# ========== API ROUTES ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/diagnose/engine', methods=['POST'])
def diagnose_engine():
    data = request.json
    symptoms = data.get('symptoms', {})
    result = engine.diagnose_engine(symptoms)
    return jsonify(result)

@app.route('/api/diagnose/battery', methods=['POST'])
def diagnose_battery():
    data = request.json
    symptoms = data.get('symptoms', {})
    result = engine.diagnose_battery(symptoms)
    return jsonify(result)

@app.route('/api/diagnose/starter', methods=['POST'])
def diagnose_starter():
    data = request.json
    symptoms = data.get('symptoms', {})
    result = engine.diagnose_starter(symptoms)
    return jsonify(result)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify({
        'total_customers': 0,
        'total_vehicles': 0,
        'total_diagnostics': 0,
        'total_revenue': 0
    })

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    return jsonify({'vehicles': []})

@app.route('/api/analytics/dashboard', methods=['GET'])
def analytics():
    return jsonify({
        'daily': {'today_diagnostics': 0, 'today_revenue': 0, 'common_issues': []},
        'technician_performance': [],
        'weekly_trends': []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ========== REGISTRATION ENDPOINT ==========
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    email = data.get('email')
    role = data.get('role', 'technician')
    
    from auth import UserManager
    um = UserManager()
    
    user_id = um.create_user(username, password, full_name, role)
    
    if user_id:
        return jsonify({'success': True, 'message': 'User created successfully', 'user_id': user_id})
    else:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
