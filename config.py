# config.py - System configuration
import os

class Config:
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'workshop.db')
    
    # API Settings
    API_HOST = '0.0.0.0'
    API_PORT = 5000
    DEBUG_MODE = True
    
    # Business Settings
    WORKSHOP_NAME = "BLESS DIGITAL AUTO CARE"
    HOURLY_RATE = 85.00  # Labor rate per hour
    TAX_RATE = 0.10  # 10% tax
    
    # File paths
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
    LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
    
    # Create directories if they don't exist
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Supported diagnostic types
    DIAGNOSTIC_TYPES = ['engine', 'battery', 'starter', 'electrical', 'transmission', 'brakes']
    
    # Severity levels
    SEVERITY_LEVELS = {
        'low': '🟢 Low - Monitor only',
        'medium': '🟡 Medium - Schedule service',
        'high': '🔴 High - Immediate attention needed',
        'critical': '💀 Critical - Do not drive'
    }
