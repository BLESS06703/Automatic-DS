import sqlite3
import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        # Use /tmp for Render, local for development
        if os.environ.get('RENDER'):
            self.db_path = '/tmp/workshop.db'
        else:
            self.db_path = 'data/workshop.db'
            os.makedirs('data', exist_ok=True)
        
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vehicles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                vin TEXT,
                make TEXT,
                model TEXT,
                year INTEGER,
                license_plate TEXT,
                mileage INTEGER DEFAULT 0,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                technician TEXT,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'technician',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            import hashlib, secrets
            salt = secrets.token_hex(16)
            hashed = f"{salt}:{hashlib.sha256(('admin123' + salt).encode()).hexdigest()}"
            cursor.execute('''
                INSERT INTO users (username, password, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', hashed, 'System Administrator', 'admin'))
        
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    
    # ========== VEHICLE METHODS ==========
    def add_vehicle(self, customer_id, make, model, year, vin='', license_plate='', mileage=0, color=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (customer_id, make, model, year, vin, license_plate, mileage, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, make, model, year, vin, license_plate, mileage, color))
        conn.commit()
        vehicle_id = cursor.lastrowid
        conn.close()
        return vehicle_id
    
    def get_vehicles(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, c.name as customer_name 
            FROM vehicles v
            LEFT JOIN customers c ON v.customer_id = c.id
            ORDER BY v.id DESC
        ''')
        vehicles = cursor.fetchall()
        conn.close()
        return [{'id': v[0], 'customer_id': v[1], 'vin': v[2], 'make': v[3], 
                 'model': v[4], 'year': v[5], 'license_plate': v[6], 
                 'mileage': v[7], 'color': v[8], 'customer_name': v[10] if len(v) > 10 else 'Unknown'} for v in vehicles]
    
    def get_vehicle(self, vehicle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
        v = cursor.fetchone()
        conn.close()
        if v:
            return {'id': v[0], 'customer_id': v[1], 'vin': v[2], 'make': v[3], 
                    'model': v[4], 'year': v[5], 'license_plate': v[6], 'mileage': v[7], 'color': v[8]}
        return None
    
    # ========== DIAGNOSTIC METHODS ==========
    def save_diagnostic(self, vehicle_id, diagnostic_type, symptoms, results, severity, tools, action_plan, technician='System'):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnostics (vehicle_id, diagnostic_type, symptoms, results, severity, tools, action_plan, technician)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, diagnostic_type, json.dumps(symptoms), results, severity, 
              json.dumps(tools), json.dumps(action_plan), technician))
        conn.commit()
        diagnostic_id = cursor.lastrowid
        conn.close()
        return diagnostic_id
    
    def get_diagnostics(self, vehicle_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if vehicle_id:
            cursor.execute('''
                SELECT d.*, v.make, v.model, v.license_plate
                FROM diagnostics d
                JOIN vehicles v ON d.vehicle_id = v.id
                WHERE d.vehicle_id = ?
                ORDER BY d.created_at DESC
            ''', (vehicle_id,))
        else:
            cursor.execute('''
                SELECT d.*, v.make, v.model, v.license_plate
                FROM diagnostics d
                JOIN vehicles v ON d.vehicle_id = v.id
                ORDER BY d.created_at DESC
                LIMIT 50
            ''')
        rows = cursor.fetchall()
        conn.close()
        
        diagnostics = []
        for row in rows:
            diagnostics.append({
                'id': row[0],
                'vehicle_id': row[1],
                'type': row[2],
                'symptoms': json.loads(row[3]) if row[3] else [],
                'results': row[4],
                'severity': row[5],
                'tools': json.loads(row[6]) if row[6] else [],
                'action_plan': json.loads(row[7]) if row[7] else [],
                'date': row[8],
                'technician': row[9],
                'vehicle': {'make': row[11], 'model': row[12], 'license_plate': row[13]}
            })
        return diagnostics
    
    # ========== CUSTOMER METHODS ==========
    def add_customer(self, name, phone='', email='', address=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, phone, email, address)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, address))
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return customer_id
    
    def get_customers(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM customers ORDER BY name')
        customers = cursor.fetchall()
        conn.close()
        return [{'id': c[0], 'name': c[1], 'phone': c[2], 'email': c[3], 'address': c[4]} for c in customers]
    
    # ========== STATISTICS ==========
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        total_vehicles = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM diagnostics")
        total_diagnostics = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM diagnostics WHERE severity = 'high'")
        high_severity = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_customers': total_customers,
            'total_vehicles': total_vehicles,
            'total_diagnostics': total_diagnostics,
            'high_severity': high_severity,
            'total_revenue': total_diagnostics * 5000  # Placeholder revenue
        }
