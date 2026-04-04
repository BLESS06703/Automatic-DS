import sqlite3
import os
import hashlib
import secrets

print("=== Initializing Database ===")

def hash_password(password):
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

# Use /tmp for Render
db_path = '/tmp/workshop.db'
print(f"Database path: {db_path}")

# Create connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table
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

# Create customers table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create vehicles table
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create diagnostics table
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Check if admin exists
cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
admin_exists = cursor.fetchone()[0]

if admin_exists == 0:
    # Create admin user
    hashed = hash_password('admin123')
    cursor.execute('''
        INSERT INTO users (username, password, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?)
    ''', ('admin', hashed, 'System Administrator', 'admin', 1))
    print("✅ Admin user created: admin / admin123")
else:
    print("✅ Admin user already exists")

# Verify
cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
user = cursor.fetchone()
if user:
    print(f"✅ Verified: {user[0]} exists with role {user[1]}")

conn.commit()
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"✅ Total users in database: {user_count}")

conn.close()
print("=== Database initialization complete ===")
