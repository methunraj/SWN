#!/bin/bash

echo "🚀 Starting Swift Neethi Application"
echo "======================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python3 is installed
if ! command_exists python3; then
    echo "❌ Python3 is required but not installed. Please install Python3."
    exit 1
fi

# Check if Node.js is installed
if ! command_exists node; then
    echo "❌ Node.js is required but not installed. Please install Node.js."
    exit 1
fi

# Check if npm is installed
if ! command_exists npm; then
    echo "❌ npm is required but not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Start backend in the background
echo ""
echo "📡 Starting Backend (FastAPI)..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Start backend server in background
echo "Starting FastAPI server on http://localhost:8000..."
python3 main.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Frontend (React)..."
cd ../frontend

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Start frontend server
echo "Starting React development server on http://localhost:3000..."
npm start &
FRONTEND_PID=$!

echo ""
echo "🎉 Swift Neethi is starting up!"
echo ""
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Shutting down Swift Neethi..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for either process to finish
wait