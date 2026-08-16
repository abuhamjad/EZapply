@echo off
REM ============================================================================
REM EZApply - Run Both Frontend and Backend (Windows Batch)
REM ============================================================================
REM This script starts both the frontend and backend servers simultaneously
REM Frontend: http://localhost:5173
REM Backend: http://localhost:8000
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo Starting EZApply (Frontend + Backend)
echo ==========================================
echo.

REM Activate virtual environment for backend
echo 📦 Activating backend environment...
call venv\Scripts\activate.bat

REM Start Backend in a new window
echo 🚀 Starting Backend (port 8000)...
start "EZApply Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

REM Start Frontend in a new window
echo 🚀 Starting Frontend (port 5173)...
start "EZApply Frontend" cmd /k "cd frontend && pnpm dev"

echo.
echo ==========================================
echo ✅ Both servers started successfully!
echo ==========================================
echo.
echo 📍 Frontend:  http://localhost:5173
echo 📍 Backend:   http://localhost:8000
echo 📍 API Docs:  http://localhost:8000/docs
echo.
echo ⚠️  Close the command windows to stop the servers
echo.

pause
