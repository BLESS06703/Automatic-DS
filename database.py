# database.py - Complete database management
import sqlite3
import json
from datetime import datetime
from config import Config
import os

class Database:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize all database tables"""
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
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vehicles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                vin TEXT UNIQUE,
                make TEXT,
                model TEXT,
                year INTEGER,
                license_plate TEXT,
                mileage INTEGER,
                color TEXT,
                engine_type TEXT,
                transmission TEXT,
                last_service DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
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
                tools TEXT,
                action_plan TEXT,
                severity TEXT DEFAULT 'low',
                labor_hours REAL DEFAULT 0,
                parts_cost REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                technician TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            )
        ''')
        
        # Service history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                service_date DATE,
                service_type TEXT,
                description TEXT,
                parts_used TEXT,
                labor_cost REAL,
                parts_cost REAL,
                total_cost REAL,
                mileage INTEGER,
                technician TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            )
        ''')
        
        # Parts inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_number TEXT UNIQUE,
                name TEXT,
                brand TEXT,
                category TEXT,
                price REAL,
                quantity INTEGER DEFAULT 0,
                location TEXT,
                min_quantity INTEGER DEFAULT 5,
                supplier TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users/Technicians table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'technician',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default technician if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'tech1'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                ('tech1', 'password123', 'John Technician', 'technician')
            )
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    # Customer operations
    def add_customer(self, name, phone="", email="", address="", notes=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (name, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, email, address, notes))
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return customer_id
    
    def get_customer(self, customer_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        if customer:
            return {
                'id': customer[0],
                'name': customer[1],
                'phone': customer[2],
                'email': customer[3],
                'address': customer[4],
                'notes': customer[5],
                'created_at': customer[6]
            }
        return None
    
    def search_customers(self, search_term):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM customers 
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        customers = cursor.fetchall()
        conn.close()
        return [{'id': c[0], 'name': c[1], 'phone': c[2], 'email': c[3]} for c in customers]
    
    # Vehicle operations
    def add_vehicle(self, customer_id, make, model, year, vin="", license_plate="", 
                    mileage=0, color="", engine_type="", transmission=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (customer_id, make, model, year, vin, license_plate, 
                                 mileage, color, engine_type, transmission)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, make, model, year, vin, license_plate, mileage, color, engine_type, transmission))
        conn.commit()
        vehicle_id = cursor.lastrowid
        conn.close()
        return vehicle_id
    
    def get_vehicle(self, vehicle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, c.name as customer_name 
            FROM vehicles v
            JOIN customers c ON v.customer_id = c.id
            WHERE v.id = ?
        ''', (vehicle_id,))
        vehicle = cursor.fetchone()
        conn.close()
        if vehicle:
            return {
                'id': vehicle[0],
                'customer_id': vehicle[1],
                'vin': vehicle[2],
                'make': vehicle[3],
                'model': vehicle[4],
                'year': vehicle[5],
                'license_plate': vehicle[6],
                'mileage': vehicle[7],
                'color': vehicle[8],
                'engine_type': vehicle[9],
                'transmission': vehicle[10],
                'last_service': vehicle[11],
                'notes': vehicle[12],
                'customer_name': vehicle[16]
            }
        return None
    
    def get_all_vehicles(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, v.make, v.model, v.year, v.license_plate, v.mileage, c.name as customer_name
            FROM vehicles v
            JOIN customers c ON v.customer_id = c.id
            ORDER BY v.id DESC
        ''')
        vehicles = cursor.fetchall()
        conn.close()
        return [{'id': v[0], 'make': v[1], 'model': v[2], 'year': v[3], 
                 'license': v[4], 'mileage': v[5], 'customer': v[6]} for v in vehicles]
    
    # Diagnostic operations
    def save_diagnostic(self, vehicle_id, diag_type, symptoms, results, tools, 
                        action_plan, severity='low', labor_hours=0, parts_cost=0, 
                        technician="Auto Tech", notes=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        total_cost = (labor_hours * Config.HOURLY_RATE) + parts_cost
        cursor.execute('''
            INSERT INTO diagnostics (vehicle_id, diagnostic_type, symptoms, results, 
                                    tools, action_plan, severity, labor_hours, 
                                    parts_cost, total_cost, technician, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, diag_type, json.dumps(symptoms), results, 
              json.dumps(tools), json.dumps(action_plan), severity, 
              labor_hours, parts_cost, total_cost, technician, notes))
        conn.commit()
        diagnostic_id = cursor.lastrowid
        conn.close()
        return diagnostic_id
    
    def get_diagnostic(self, diagnostic_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, v.make, v.model, v.year, v.vin, v.license_plate, v.mileage, c.name as customer_name
            FROM diagnostics d
            JOIN vehicles v ON d.vehicle_id = v.id
            JOIN customers c ON v.customer_id = c.id
            WHERE d.id = ?
        ''', (diagnostic_id,))
        record = cursor.fetchone()
        conn.close()
        
        if record:
            return {
                'id': record[0],
                'vehicle_id': record[1],
                'diagnostic_type': record[2],
                'symptoms': json.loads(record[3]) if record[3] else [],
                'results': record[4],
                'tools': json.loads(record[5]) if record[5] else [],
                'action_plan': json.loads(record[6]) if record[6] else [],
                'severity': record[7],
                'labor_hours': record[8],
                'parts_cost': record[9],
                'total_cost': record[10],
                'status': record[11],
                'technician': record[12],
                'created_at': record[13],
                'notes': record[15],
                'vehicle': {
                    'make': record[16],
                    'model': record[17],
                    'year': record[18],
                    'vin': record[19],
                    'license_plate': record[20],
                    'mileage': record[21]
                },
                'customer_name': record[22]
            }
        return None
    
    def get_vehicle_history(self, vehicle_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, diagnostic_type, severity, status, created_at, technician
            FROM diagnostics 
            WHERE vehicle_id = ? 
            ORDER BY created_at DESC
        ''', (vehicle_id,))
        records = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'type': r[1], 'severity': r[2], 
                 'status': r[3], 'date': r[4], 'technician': r[5]} for r in records]
    
    def update_diagnostic_status(self, diagnostic_id, status, completed_at=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if completed_at:
            cursor.execute('''
                UPDATE diagnostics 
                SET status = ?, completed_at = ?
                WHERE id = ?
            ''', (status, completed_at, diagnostic_id))
        else:
            cursor.execute('''
                UPDATE diagnostics 
                SET status = ?
                WHERE id = ?
            ''', (status, diagnostic_id))
        conn.commit()
        conn.close()
    
    # Statistics
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total customers
        cursor.execute("SELECT COUNT(*) FROM customers")
        stats['total_customers'] = cursor.fetchone()[0]
        
        # Total vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        stats['total_vehicles'] = cursor.fetchone()[0]
        
        # Total diagnostics
        cursor.execute("SELECT COUNT(*) FROM diagnostics")
        stats['total_diagnostics'] = cursor.fetchone()[0]
        
        # Revenue (completed diagnostics)
        cursor.execute("SELECT SUM(total_cost) FROM diagnostics WHERE status = 'completed'")
        stats['total_revenue'] = cursor.fetchone()[0] or 0
        
        # Pending diagnostics
        cursor.execute("SELECT COUNT(*) FROM diagnostics WHERE status = 'pending'")
        stats['pending_diagnostics'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def close(self):
        pass  # Connections are handled per operation
