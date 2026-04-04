from flask import Flask, request, jsonify, send_file, redirect, session
from flask_cors import CORS
from database import Database
from diagnostic_engine import DiagnosticEngine
from report_generator import ReportGenerator
from config import Config
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ========== AUTHENTICATION SETUP ==========
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import UserManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page'

user_manager = UserManager()

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user(int(user_id))


# ========== AUTHENTICATION ENDPOINTS ==========

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = user_manager.authenticate(username, password)
    
    if user:
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'role': user.role
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user (admin only in production)"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name')
    role = data.get('role', 'technician')
    
    user_id = user_manager.create_user(username, password, full_name, role)
    
    if user_id:
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': user_id
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Username already exists'
        }), 400

@app.route('/api/current-user', methods=['GET'])
@login_required
def current_user_info():
    """Get current logged in user info"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'full_name': current_user.full_name,
        'role': current_user.role,
        'is_authenticated': True
    })

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': current_user.username,
                'full_name': current_user.full_name,
                'role': current_user.role
            }
        })
    return jsonify({'authenticated': False})

db = Database()
engine = DiagnosticEngine()

# ========== WEB INTERFACE ROUTES ==========
@app.route('/')
def home():
    return redirect('/web_interface.html')

@app.route('/web_interface.html')
def serve_web_interface():
    """Serve the main web interface"""
    web_file = os.path.join(os.path.dirname(__file__), 'web_interface.html')
    if os.path.exists(web_file):
        return send_file(web_file)
    return "web_interface.html not found. Please check the file exists.", 404

# ========== STATIC FILES ==========
@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js')

# ========== API INFO ==========
@app.route('/api')
def api_info():
    return jsonify({
        'system': 'Bless Digital Auto Care',
        'version': '2.0',
        'status': 'online',
        'endpoints': {
            'web_interface': '/web_interface.html',
            'health': '/api/health',
            'diagnose_engine': '/api/diagnose/engine (POST)',
            'diagnose_battery': '/api/diagnose/battery (POST)',
            'diagnose_starter': '/api/diagnose/starter (POST)',
            'vehicles': '/api/vehicles (GET)',
            'statistics': '/api/statistics (GET)',
            'add_customer': '/api/customer/add (POST)',
            'add_vehicle': '/api/vehicle/add (POST)'
        }
    })

# ========== HEALTH CHECK ==========
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })

# ========== DIAGNOSTIC ENDPOINTS ==========
@app.route('/api/diagnose/engine', methods=['POST'])
def diagnose_engine():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    diagnosis = engine.diagnose_engine(symptoms)
    
    if vehicle_id:
        diagnostic_id = db.save_diagnostic(
            vehicle_id=vehicle_id,
            diag_type='engine',
            symptoms=diagnosis['symptoms'],
            results=diagnosis['results'],
            tools=diagnosis['tools'],
            action_plan=diagnosis['action_plan'],
            severity=diagnosis['severity'],
            labor_hours=data.get('labor_hours', 1.5),
            technician=data.get('technician', 'Auto Tech'),
            notes=data.get('notes', '')
        )
        diagnosis['diagnostic_id'] = diagnostic_id
    
    return jsonify(diagnosis)

@app.route('/api/diagnose/battery', methods=['POST'])
def diagnose_battery():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    diagnosis = engine.diagnose_battery(symptoms)
    
    if vehicle_id:
        diagnostic_id = db.save_diagnostic(
            vehicle_id=vehicle_id,
            diag_type='battery',
            symptoms=diagnosis['symptoms'],
            results=diagnosis['results'],
            tools=diagnosis['tools'],
            action_plan=diagnosis['action_plan'],
            severity=diagnosis['severity'],
            labor_hours=data.get('labor_hours', 1.0),
            technician=data.get('technician', 'Auto Tech'),
            notes=data.get('notes', '')
        )
        diagnosis['diagnostic_id'] = diagnostic_id
    
    return jsonify(diagnosis)

@app.route('/api/diagnose/starter', methods=['POST'])
def diagnose_starter():
    data = request.json
    symptoms = data.get('symptoms', {})
    vehicle_id = data.get('vehicle_id')
    
    diagnosis = engine.diagnose_starter(symptoms)
    
    if vehicle_id:
        diagnostic_id = db.save_diagnostic(
            vehicle_id=vehicle_id,
            diag_type='starter',
            symptoms=diagnosis['symptoms'],
            results=diagnosis['results'],
            tools=diagnosis['tools'],
            action_plan=diagnosis['action_plan'],
            severity=diagnosis['severity'],
            labor_hours=data.get('labor_hours', 1.5),
            technician=data.get('technician', 'Auto Tech'),
            notes=data.get('notes', '')
        )
        diagnosis['diagnostic_id'] = diagnostic_id
    
    return jsonify(diagnosis)

# ========== CUSTOMER ENDPOINTS ==========
@app.route('/api/customer/add', methods=['POST'])
def add_customer():
    data = request.json
    customer_id = db.add_customer(
        name=data.get('name'),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', ''),
        notes=data.get('notes', '')
    )
    return jsonify({'success': True, 'customer_id': customer_id})

@app.route('/api/vehicle/add', methods=['POST'])
def add_vehicle():
    data = request.json
    vehicle_id = db.add_vehicle(
        customer_id=data.get('customer_id'),
        make=data.get('make'),
        model=data.get('model'),
        year=data.get('year'),
        vin=data.get('vin', ''),
        license_plate=data.get('license_plate', ''),
        mileage=data.get('mileage', 0),
        color=data.get('color', ''),
        engine_type=data.get('engine_type', ''),
        transmission=data.get('transmission', '')
    )
    return jsonify({'success': True, 'vehicle_id': vehicle_id})

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = db.get_all_vehicles()
    return jsonify({'vehicles': vehicles})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/report/generate/<int:diagnostic_id>', methods=['GET'])
def generate_report(diagnostic_id):
    diagnostic = db.get_diagnostic(diagnostic_id)
    if not diagnostic:
        return jsonify({'error': 'Diagnostic not found'}), 404
    
    vehicle_info = {
        'make': diagnostic['vehicle']['make'],
        'model': diagnostic['vehicle']['model'],
        'year': diagnostic['vehicle']['year'],
        'vin': diagnostic['vehicle']['vin'],
        'license_plate': diagnostic['vehicle']['license_plate'],
        'mileage': diagnostic['vehicle']['mileage'],
        'customer': diagnostic['customer_name']
    }
    
    diagnosis_data = {
        'symptoms': diagnostic['symptoms'],
        'results': diagnostic['results'],
        'tools': diagnostic['tools'],
        'action_plan': diagnostic['action_plan'],
        'severity': diagnostic['severity']
    }
    
    cost_estimate = {
        'labor_hours': diagnostic['labor_hours'],
        'parts_cost': diagnostic['parts_cost']
    }
    
    report = ReportGenerator(f"report_{diagnostic_id}.txt")
    filename = report.generate(
        vehicle_info=vehicle_info,
        diagnosis=diagnosis_data,
        cost_estimate=cost_estimate,
        technician_notes=diagnostic.get('notes', '')
    )
    
    return send_file(filename, as_attachment=True)

# ========== MAIN ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
