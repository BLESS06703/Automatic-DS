#!/bin/bash
PORT=3000

# Kill any existing server on the port
pkill -f "python -m http.server $PORT" 2>/dev/null

echo "🌍 Starting web server on port $PORT..."
echo "📱 Open http://localhost:$PORT/web_interface.html in your browser"
echo "Press Ctrl+C to stop"
echo ""

python -m http.server $PORT
