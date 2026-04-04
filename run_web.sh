#!/bin/bash
# Start simple web server for the HTML interface

echo "🌍 Starting web server on port 8080..."
echo "📱 Open http://localhost:8080/web_interface.html in your browser"
echo "Press Ctrl+C to stop"
echo ""

python -m http.server 8080
