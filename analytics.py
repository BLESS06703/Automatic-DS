# analytics.py - Business analytics and dashboard
from database import Database
from datetime import datetime, timedelta
import json

class Analytics:
    def __init__(self):
        self.db = Database()
    
    def get_daily_stats(self):
        """Get today's statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Today's diagnostics
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(total_cost), 0)
            FROM diagnostics 
            WHERE DATE(created_at) = ?
        """, (today,))
        today_diagnostics, today_revenue = cursor.fetchone()
        
        # Most common issues
        cursor.execute("""
            SELECT diagnostic_type, COUNT(*) as count
            FROM diagnostics 
            WHERE DATE(created_at) >= DATE('now', '-30 days')
            GROUP BY diagnostic_type
            ORDER BY count DESC
        """)
        common_issues = cursor.fetchall()
        
        conn.close()
        
        return {
            'today_diagnostics': today_diagnostics or 0,
            'today_revenue': today_revenue or 0,
            'common_issues': [{'type': i[0], 'count': i[1]} for i in common_issues]
        }
    
    def get_weekly_trends(self):
        """Get weekly diagnostic trends"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count,
                SUM(total_cost) as revenue
            FROM diagnostics 
            WHERE created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        trends = cursor.fetchall()
        conn.close()
        
        return [{'date': t[0], 'count': t[1], 'revenue': t[2]} for t in trends]
    
    def get_technician_performance(self):
        """Track technician performance"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                technician,
                COUNT(*) as diagnostics_count,
                AVG(labor_hours) as avg_hours,
                SUM(total_cost) as total_revenue
            FROM diagnostics 
            WHERE created_at >= DATE('now', '-30 days')
            GROUP BY technician
            ORDER BY diagnostics_count DESC
        """)
        
        performance = cursor.fetchall()
        conn.close()
        
        return [{
            'technician': p[0],
            'diagnostics': p[1],
            'avg_hours': round(p[2], 2) if p[2] else 0,
            'revenue': p[3] or 0
        } for p in performance]
