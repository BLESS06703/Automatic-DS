# qr_service.py - Generate QR codes without Pillow
import segno
import os
from datetime import datetime

class QRService:
    def __init__(self, qr_dir="static/qrcodes"):
        self.qr_dir = qr_dir
        os.makedirs(self.qr_dir, exist_ok=True)
    
    def generate_vehicle_qr(self, vehicle_id, vehicle_info):
        """Generate QR code that links to vehicle history"""
        # Create data to encode
        qr_data = f"Vehicle: {vehicle_info['make']} {vehicle_info['model']} ({vehicle_info['year']})\nID: {vehicle_id}"
        
        # Generate QR code
        qr = segno.make(qr_data)
        
        # Save as PNG (segno handles it without Pillow)
        filename = f"vehicle_{vehicle_id}_{datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(self.qr_dir, filename)
        qr.save(filepath, scale=5)
        
        return filepath
    
    def generate_diagnostic_qr(self, diagnostic_id):
        """Generate QR code for specific diagnostic report"""
        qr_data = f"Diagnostic Report ID: {diagnostic_id}"
        
        qr = segno.make(qr_data)
        
        filename = f"diagnostic_{diagnostic_id}.png"
        filepath = os.path.join(self.qr_dir, filename)
        qr.save(filepath, scale=5)
        
        return filepath
    
    def generate_text_qr(self, text):
        """Generate QR code from any text"""
        qr = segno.make(text)
        filename = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.qr_dir, filename)
        qr.save(filepath, scale=5)
        return filepath
