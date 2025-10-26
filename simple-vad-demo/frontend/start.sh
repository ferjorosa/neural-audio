#!/bin/bash

# Simple VAD Demo - Frontend Startup Script

echo "🚀 Starting Simple VAD Demo Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting Next.js development server on http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
