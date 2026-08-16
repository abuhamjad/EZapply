#!/bin/bash

# ============================================================================
# EZApply - Run Both Frontend and Backend
# ============================================================================
# This script starts both the frontend and backend servers simultaneously
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Starting EZApply (Frontend + Backend)"
echo "=========================================="
echo ""

# Activate virtual environment for backend
echo "📦 Activating backend environment..."
source "$SCRIPT_DIR/venv/bin/activate" 2>/dev/null || echo "⚠️  Virtual environment not found. Make sure to create it with: python -m venv venv"

# Start Backend
echo "🚀 Starting Backend (port 8000)..."
cd "$SCRIPT_DIR/backend"
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "🚀 Starting Frontend (port 5173)..."
cd "$SCRIPT_DIR/frontend"
pnpm dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "✅ Both servers started successfully!"
echo "=========================================="
echo ""
echo "📍 Frontend:  http://localhost:5173"
echo "📍 Backend:   http://localhost:8000"
echo "📍 API Docs:  http://localhost:8000/docs"
echo ""
echo "PIDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "⚠️  To stop the servers, press Ctrl+C"
echo ""

# Handle Ctrl+C gracefully
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
