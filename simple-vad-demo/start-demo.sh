#!/bin/bash

# Simple VAD Demo - Complete Startup Script
# This script starts both backend and frontend in separate terminals

echo "🎤 Simple VAD Demo - Complete Startup"
echo "====================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the simple-vad-demo directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "📋 Starting components..."
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command_exists uv; then
    echo "❌ uv is required but not installed"
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Start backend in background
echo "🔧 Starting backend server..."
cd backend
if [ -f "start.sh" ]; then
    ./start.sh &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
else
    echo "❌ Backend start script not found"
    exit 1
fi
cd ..

# Wait a moment for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
if [ -f "start.sh" ]; then
    ./start.sh &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
else
    echo "❌ Frontend start script not found"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi
cd ..

echo ""
echo "🚀 Simple VAD Demo is starting up!"
echo ""
echo "📡 Backend:  http://localhost:8000"
echo "🌐 Frontend: http://localhost:3001"
echo ""
echo "⏳ Please wait a moment for both servers to fully initialize..."
echo "   Then open http://localhost:3001 in your browser"
echo ""
echo "🛑 To stop both servers, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
