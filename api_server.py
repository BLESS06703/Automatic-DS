from flask import Flask, request, jsonify, send_file, redirect
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
db = Database()
engine = DiagnosticEngine()

# ========== ROOT REDIRECT TO WEB INTERFACE ==========
@app.route('/')
def home():
    """Redirect to the web interface"""
    return redirect('/web_interface.html')

# ========== STATIC FILES (for PWA) ==========
@app.route('/manifest.json')
def serve_manifest():
    """Serve PWA manifest"""
    return send_file('manifest.json')

@app.route('/sw.js')
def serve_sw():
    """Serve service worker"""
    return send_file('sw.js')

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

@app.route('/api/customer/search', methods=['GET'])
def search_customers():
    search_term = request.args.get('q', '')
    customers = db.search_customers(search_term)
    return jsonify({'customers': customers})

@app.route('/api/customer/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = db.get_customer(customer_id)
    if customer:
        return jsonify(customer)
    return jsonify({'error': 'Customer not found'}), 404

# ========== VEHICLE ENDPOINTS ==========
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

@app.route('/api/vehicle/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = db.get_vehicle(vehicle_id)
    if vehicle:
        return jsonify(vehicle)
    return jsonify({'error': 'Vehicle not found'}), 404

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = db.get_all_vehicles()
    return jsonify({'vehicles': vehicles})

# ========== HISTORY & REPORTS ==========
@app.route('/api/history/<int:vehicle_id>', methods=['GET'])
def get_history(vehicle_id):
    history = db.get_vehicle_history(vehicle_id)
    return jsonify({'history': history})

@app.route('/api/diagnostic/<int:diagnostic_id>', methods=['GET'])
def get_diagnostic(diagnostic_id):
    diagnostic = db.get_diagnostic(diagnostic_id)
    if diagnostic:
        return jsonify(diagnostic)
    return jsonify({'error': 'Diagnostic not found'}), 404

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

# ========== STATISTICS ==========
@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    stats = db.get_statistics()
    return jsonify(stats)

# ========== API INFO ==========
@app.route('/api', methods=['GET'])
def api_info():
    return jsonify({
        'system': Config.WORKSHOP_NAME,
        'version': '2.0',
        'status': 'online',
        'endpoints': {
            'web_interface': '/',
            'api_docs': '/api',
            'health': '/api/health',
            'diagnose': {
                'engine': '/api/diagnose/engine (POST)',
                'battery': '/api/diagnose/battery (POST)',
                'starter': '/api/diagnose/starter (POST)'
            },
            'customers': {
                'add': '/api/customer/add (POST)',
                'search': '/api/customer/search (GET)',
                'get': '/api/customer/<id> (GET)'
            },
            'vehicles': {
                'add': '/api/vehicle/add (POST)',
                'get': '/api/vehicle/<id> (GET)',
                'list': '/api/vehicles (GET)'
            },
            'reports': {
                'generate': '/api/report/generate/<diagnostic_id> (GET)'
            },
            'history': '/api/history/<vehicle_id> (GET)',
            'statistics': '/api/statistics (GET)'
        }
    })

# ========== MAIN ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)