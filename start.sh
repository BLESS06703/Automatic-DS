#!/bin/bash

# Bless Digital Auto Care - Startup Script
# Professional Car Diagnostic System

echo "=========================================="
echo "   BLESS DIGITAL AUTO CARE"
echo "   Professional Diagnostic System"
echo "=========================================="
echo ""

# Check Python installation
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Installing..."
    pkg install python -y
fi

# Check and install required packages
echo "📦 Checking dependencies..."
if ! python -c "import flask" &> /dev/null; then
    echo "Installing Flask..."
    pip install flask flask-cors
fi

# Create necessary directories
mkdir -p data reports logs

# Run system test
echo ""
echo "🔍 Running system test..."
python -c "
import sys
try:
    from database import Database
    from diagnostic_engine import DiagnosticEngine
    from report_generator import ReportGenerator
    from config import Config
    print('✅ All modules loaded successfully')
    print(f'✅ Database path: {Config.DATABASE_PATH}')
    print(f'✅ Reports directory: {Config.REPORTS_DIR}')
    sys.exit(0)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ System ready!"
    echo ""
    echo "=========================================="
    echo "🌐 Starting API Server..."
    echo "📍 API: http://localhost:5000"
    echo "🌍 Web Interface: http://localhost:5000 (or open web_interface.html)"
    echo "=========================================="
    echo ""
    echo "💡 To use the web interface:"
    echo "   Option 1: Open web_interface.html in browser"
    echo "   Option 2: Run 'python -m http.server 8080' and visit http://localhost:8080"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the API server
    python api_server.py
else
    echo ""
    echo "❌ System test failed. Please check the errors above."
    exit 1
fi
