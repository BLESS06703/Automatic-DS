# auth.py - User authentication module (using hashlib - no extra dependencies!)
from flask_login import UserMixin
from database import Database
import hashlib
import secrets
import sqlite3

class User(UserMixin):
    def __init__(self, id, username, full_name, role):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role

class UserManager:
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password):
        """Hash password using SHA-256 (no extra dependencies needed)"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((password + salt).encode())
        return f"{salt}:{hash_obj.hexdigest()}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, hash_value = stored_hash.split(':')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return test_hash == hash_value
        except:
            return False
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role FROM users WHERE id = ? AND is_active = 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(row[0], row[1], row[2], row[3])
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, password FROM users WHERE username = ? AND is_active = 1", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = User(row[0], row[1], row[2], row[3])
            user.password_hash = row[4]
            return user
        return None
    
    def authenticate(self, username, password):
        """Authenticate user"""
        user = self.get_user_by_username(username)
        if user and hasattr(user, 'password_hash'):
            if self.verify_password(password, user.password_hash):
                return user
        return None
    
    def create_user(self, username, password, full_name, role='technician'):
        """Create new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            hashed = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', (username, hashed, full_name, role))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    def change_password(self, username, old_password, new_password):
        """Change user password"""
        user = self.authenticate(username, old_password)
        if user:
            new_hashed = self.hash_password(new_password)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_hashed, username))
            conn.commit()
            conn.close()
            return True
        return False
