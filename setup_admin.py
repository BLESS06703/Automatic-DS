import sqlite3
import hashlib
import secrets
import os

def hash_password(password):
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

# Use the same path as Render
db_path = '/tmp/workshop.db'
print(f"Connecting to database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    print("Creating users table...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'technician',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

# Delete existing admin
cursor.execute("DELETE FROM users WHERE username = 'admin'")

# Create new admin
hashed = hash_password('admin123')
cursor.execute('''
    INSERT INTO users (username, password, full_name, role, is_active)
    VALUES (?, ?, ?, ?, ?)
''', ('admin', hashed, 'System Administrator', 'admin', 1))

conn.commit()

# Verify
cursor.execute("SELECT username, role FROM users WHERE username = 'admin'")
user = cursor.fetchone()
if user:
    print(f"✅ Admin user created: {user[0]} / admin123 (role: {user[1]})")
else:
    print("❌ Failed to create admin")

conn.close()
