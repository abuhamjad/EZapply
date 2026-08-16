# 🚀 Quick Start Guide - Running EZApply

## Run Everything in One Command

### **Windows (PowerShell - Recommended)**
```powershell
.\run_all.ps1
```

**First time setup:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\run_all.ps1
```

### **Windows (Command Prompt / Batch)**
```cmd
run_all.bat
```

### **macOS / Linux (Bash)**
```bash
chmod +x run_all.sh
./run_all.sh
```

---

## What Gets Started

| Service   | URL                      | Purpose                |
|-----------|--------------------------|------------------------|
| Frontend  | http://localhost:5173    | React UI               |
| Backend   | http://localhost:8000    | FastAPI Server         |
| Docs      | http://localhost:8000/docs | API Documentation      |

---

## Individual Commands (if needed)

### Backend Only
```powershell
# Windows PowerShell (recommended)
.\run_backend.ps1

# Windows - Direct command
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

```bash
# macOS / Linux
./run_backend.sh
```

### Frontend Only
```powershell
cd frontend
pnpm dev
```

---

## Troubleshooting

### Backend starts but Frontend doesn't
- Make sure dependencies are installed: `cd frontend && pnpm install`

### Virtual environment error
- Create it: `python -m venv venv`
- Activate it: `.\venv\Scripts\activate.ps1` (PowerShell) or `venv\Scripts\activate.bat` (CMD)

### Port already in use
- Backend: Change port in `run_backend.ps1` or `run_backend.sh`
- Frontend: Change port in `frontend/vite.config.ts`

### Permission denied on macOS/Linux
- Make scripts executable:
  ```bash
  chmod +x run_all.sh run_backend.sh
  ```

---

## Stop the Servers

### PowerShell
```powershell
Stop-Job -Name EZApply-Backend
Stop-Job -Name EZApply-Frontend
```

### Batch / Command Prompt
- Close the command windows manually

### Bash
- Press `Ctrl+C` in the terminal

---

## Next Steps

1. Open http://localhost:5173 in your browser
2. Check API docs at http://localhost:8000/docs
3. Start building! 🎉
