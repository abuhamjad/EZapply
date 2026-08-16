# ============================================================================
# EZApply - Run Both Frontend and Backend
# ============================================================================
# This script starts both the frontend and backend servers simultaneously
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# ============================================================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Starting EZApply (Frontend + Backend)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment for backend
Write-Host "📦 Activating backend environment..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

# Start Backend in a background job
Write-Host "🚀 Starting Backend (port 8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location -Path "$using:PSScriptRoot\backend"
    python -m uvicorn app.main:app --reload --port 8000
} -Name "EZApply-Backend"

# Start Frontend in a background job
Write-Host "🚀 Starting Frontend (port 5173)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location -Path "$using:PSScriptRoot\frontend"
    pnpm dev
} -Name "EZApply-Frontend"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Both servers started successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Frontend:  http://localhost:5173" -ForegroundColor Magenta
Write-Host "📍 Backend:   http://localhost:8000" -ForegroundColor Magenta
Write-Host "📍 API Docs:  http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host ""
Write-Host "Job IDs:" -ForegroundColor Yellow
Write-Host "  Backend:  $($backendJob.Id)" -ForegroundColor Gray
Write-Host "  Frontend: $($frontendJob.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  To stop the servers, run: " -ForegroundColor Yellow
Write-Host "   Stop-Job -Name EZApply-Backend; Stop-Job -Name EZApply-Frontend" -ForegroundColor Gray
Write-Host ""

# Keep the script running and show output
Write-Host "Streaming logs..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Wait for jobs to complete or until interrupted
try {
    Get-Job -Name "EZApply-Backend", "EZApply-Frontend" | Wait-Job
} catch {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Name "EZApply-Backend" -ErrorAction SilentlyContinue
    Stop-Job -Name "EZApply-Frontend" -ErrorAction SilentlyContinue
    Remove-Job -Name "EZApply-Backend" -ErrorAction SilentlyContinue
    Remove-Job -Name "EZApply-Frontend" -ErrorAction SilentlyContinue
}
