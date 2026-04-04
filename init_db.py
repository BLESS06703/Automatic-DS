import sqlite3
import os
import hashlib
import secrets

def hash_password(password):
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

# Use /tmp for Render
db_path = '/tmp/workshop.db'

print(f"Initializing database at {db_path}")

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

# Create other tables as needed
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        vin TEXT,
        make TEXT,
        model TEXT,
        year INTEGER,
        license_plate TEXT,
        mileage INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create admin user
cursor.execute("DELETE FROM users WHERE username = 'admin'")
hashed = hash_password('admin123')
cursor.execute('''
    INSERT INTO users (username, password, full_name, role, is_active)
    VALUES (?, ?, ?, ?, ?)
''', ('admin', hashed, 'System Administrator', 'admin', 1))

conn.commit()
print("✅ Database initialized with admin user (admin/admin123)")

# Verify
cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
user = cursor.fetchone()
if user:
    print(f"✅ Verified: {user[0]} exists")

conn.close()
