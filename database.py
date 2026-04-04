import sqlite3
import json
import os
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        """Initialize database connection"""
        # Check if running on Render (cloud) or locally
        if os.environ.get('RENDER'):
            # On Render, use /tmp directory (writable)
            self.db_path = 'workshop.db'
            print(f"Render mode: Using database at {self.db_path}")
        else:
            # Local development - use data folder
            self.db_path = os.path.join('data', 'workshop.db')
            os.makedirs('data', exist_ok=True)
            print(f"Local mode: Using database at {self.db_path}")
        
        # Initialize database
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize all database tables"""
        try:
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
                    vin TEXT,
                    make TEXT,
                    model TEXT,
                    year INTEGER,
                    license_plate TEXT,
                    mileage INTEGER DEFAULT 0,
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
                    labor_hours REAL DEFAULT 1.0,
                    parts_cost REAL DEFAULT 0,
                    total_cost REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    technician TEXT DEFAULT 'Auto Tech',
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
                    service_date DATE DEFAULT CURRENT_DATE,
                    service_type TEXT,
                    description TEXT,
                    parts_used TEXT,
                    labor_cost REAL DEFAULT 0,
                    parts_cost REAL DEFAULT 0,
                    total_cost REAL DEFAULT 0,
                    mileage INTEGER,
                    technician TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
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
            
            # Parts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_number TEXT UNIQUE,
                    name TEXT NOT NULL,
                    brand TEXT,
                    category TEXT,
                    price REAL DEFAULT 0,
                    quantity INTEGER DEFAULT 0,
                    location TEXT,
                    min_quantity INTEGER DEFAULT 5,
                    supplier TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default data if not exists
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO customers (id, name, phone, notes) VALUES (1, 'Walk-in Customer', 'N/A', 'Default customer')")
            
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO vehicles (id, customer_id, make, model, year, license_plate) VALUES (1, 1, 'Generic', 'Vehicle', 2000, 'N/A')")
            
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO users (id, username, password, full_name, role) VALUES (1, 'tech1', 'password123', 'Master Technician', 'admin')")
            
            conn.commit()
            conn.close()
            print("✅ Database initialized successfully!")
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise
    
    # ========== CUSTOMER METHODS ==========
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
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'name': row[1], 'phone': row[2], 'email': row[3], 
                    'address': row[4], 'notes': row[5], 'created_at': row[6]}
        return None
    
    def search_customers(self, search_term):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, phone, email FROM customers 
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            LIMIT 20
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'name': r[1], 'phone': r[2], 'email': r[3]} for r in rows]
    
    # ========== VEHICLE METHODS ==========
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
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'id': row[0], 'customer_id': row[1], 'vin': row[2], 'make': row[3],
                    'model': row[4], 'year': row[5], 'license_plate': row[6], 'mileage': row[7],
                    'color': row[8], 'engine_type': row[9], 'transmission': row[10],
                    'customer_name': row[16] if len(row) > 16 else 'Unknown'}
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
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'make': r[1], 'model': r[2], 'year': r[3], 
                 'license': r[4], 'mileage': r[5], 'customer': r[6]} for r in rows]
    
    # ========== DIAGNOSTIC METHODS ==========
    def save_diagnostic(self, vehicle_id, diag_type, symptoms, results, tools, 
                        action_plan, severity='low', labor_hours=0, parts_cost=0, 
                        technician="Auto Tech", notes=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        total_cost = (labor_hours * 85) + parts_cost
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
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'vehicle_id': row[1],
                'diagnostic_type': row[2],
                'symptoms': json.loads(row[3]) if row[3] else [],
                'results': row[4],
                'tools': json.loads(row[5]) if row[5] else [],
                'action_plan': json.loads(row[6]) if row[6] else [],
                'severity': row[7],
                'labor_hours': row[8],
                'parts_cost': row[9],
                'total_cost': row[10],
                'status': row[11],
                'technician': row[12],
                'created_at': row[13],
                'notes': row[15],
                'vehicle': {
                    'make': row[16],
                    'model': row[17],
                    'year': row[18],
                    'vin': row[19],
                    'license_plate': row[20],
                    'mileage': row[21]
                },
                'customer_name': row[22]
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
            LIMIT 20
        ''', (vehicle_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{'id': r[0], 'type': r[1], 'severity': r[2], 
                 'status': r[3], 'date': r[4], 'technician': r[5]} for r in rows]
    
    # ========== STATISTICS METHODS ==========
    def get_statistics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM customers")
        stats['total_customers'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        stats['total_vehicles'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM diagnostics")
        stats['total_diagnostics'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(total_cost) FROM diagnostics WHERE status = 'completed'")
        stats['total_revenue'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM diagnostics WHERE status = 'pending'")
        stats['pending_diagnostics'] = cursor.fetchone()[0] or 0
        
        conn.close()
        return stats

# Make sure database file exists when app starts
def ensure_db_exists(self):
    """Ensure database file exists"""
    if not os.path.exists(self.db_path):
        print(f"Creating database at {self.db_path}")
        self.init_database()
