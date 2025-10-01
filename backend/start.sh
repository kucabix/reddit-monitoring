#!/bin/bash

# Start Backend Script for Reddit Agent MVP
echo "🚀 Starting Reddit Agent Backend..."

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi, uvicorn" 2>/dev/null || {
    echo "📦 Installing dependencies..."
    python3 -m pip install -r requirements.txt
}

# Start the backend
echo "🌐 Starting backend on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
