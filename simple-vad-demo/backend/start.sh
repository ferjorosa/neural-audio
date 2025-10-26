#!/bin/bash

# Simple VAD Demo - Backend Startup Script

echo "🚀 Starting Simple VAD Demo Backend..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Install dependencies using uv (no editable install)
echo "📥 Installing dependencies with uv..."
uv sync --no-editable

# Start the server using uv run
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📡 WebSocket endpoint: ws://localhost:8000/ws"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uv run python main.py
