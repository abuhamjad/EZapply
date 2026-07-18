# EZApply

**AI-Powered Job Application Automation System**

EZApply automates job search and applications on LinkedIn and Naukri.com. Combines resume parsing, AI-assisted profile analysis, automated form filling, and browser automation.

---

## Overview

EZApply reduces repetitive manual work:

- Parse resumes and extract relevant information
- Generate job search keywords from candidate profiles
- Search for relevant opportunities
- Complete application forms
- Manage user responses for recurring application questions
- Apply to jobs across multiple platforms

Architecture: React + TypeScript frontend, FastAPI Python backend, SQLite database.

---

## Key Features

### Resume Parsing

- Upload PDF, DOCX, or TXT resumes
- Extract contact information automatically
- Identify skills, experience, education, and keywords
- Generate structured candidate profiles using AI

### Intelligent Job Search

- Generate job search keywords from resume data
- Search jobs based on skills and career profile
- Support multiple locations and experience levels
- Apply company and title blacklists

### Automated Job Applications

- LinkedIn Easy Apply automation
- Naukri.com job application automation
- Automatic resume upload
- Multi-step application handling

### Smart Form Filling

- Auto-fill common fields: name, email, phone, location, LinkedIn profile URL

### Interactive User Assistance

When application forms require information that cannot be extracted automatically, the system prompts the user for input through the dashboard:

- Notice period
- Current compensation
- Expected salary
- Work authorization status

### Persistent Answer Memory

- Stores user responses locally
- Reuses previously provided answers
- Eliminates repetitive form completion

### Session Persistence

- Saves authentication cookies
- Restores login sessions between runs
- Reduces repeated login requirements

---

## Project Structure

```
EZApply/
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/routes/       # API route handlers
│   │   ├── core/             # Config, logging, constants
│   │   ├── database/         # SQLAlchemy engine & session
│   │   ├── models/           # SQLAlchemy entities
│   │   ├── repositories/     # Data access layer
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic layer
│   │   └── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   └── .env
│
├── frontend/                 # React + Vite + Tailwind CSS frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/         # Hooks, services, types
│   │   │   ├── components/   # Shared UI components
│   │   │   └── pages/        # Route pages
│   │   └── main.tsx
│   └── package.json
│
├── app.py                    # Legacy Flask backend (backward compat)
├── bot_manager.py            # Browser automation coordinator
├── linkedin_bot.py           # LinkedIn automation logic
├── naukri_bot.py             # Naukri automation logic
├── resume_parser.py          # Resume extraction and AI analysis
├── ai_matcher.py             # Job matching and AI utilities
├── constants.py              # Configuration values and defaults
├── requirements.txt          # Python dependencies
├── cookies/                  # Login session cookies
├── data/                     # Application tracking data
└── user_answers.json         # User-provided application answers
```

### Core Modules

| File             | Description                          |
| ---------------- | ------------------------------------ |
| backend/app/main.py | FastAPI backend server            |
| app.py           | Legacy Flask backend (backward compat) |
| bot_manager.py   | Coordinates bot execution and events |
| linkedin_bot.py  | LinkedIn automation logic            |
| naukri_bot.py    | Naukri automation logic              |
| resume_parser.py | Resume extraction and AI analysis    |
| ai_matcher.py    | Job matching and AI utilities        |
| constants.py     | Configuration values and defaults    |

---

## Auto-Generated Files

| File / Folder     | Purpose                                  |
| ----------------- | ---------------------------------------- |
| user_answers.json | Stores user-provided application answers |
| cookies/          | Stores login session cookies             |
| data/             | Stores application tracking information  |
| **pycache**/      | Python bytecode cache                    |

These files can be safely removed if a reset is required.

---

# Installation

## Prerequisites

- Python 3.9 or later
- Google Chrome (latest version)
- Node.js 18+ and pnpm
- Groq API Key (optional)

---

## Clone Repository

```bash
git clone https://github.com/your-username/EZApply.git
cd EZApply
```

---

## Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Frontend Dependencies

```bash
cd frontend
pnpm install
cd ..
```

---

## Add Resume

Place your resume inside the `resumes` directory:

```
resumes/
└── Resume.pdf
```

Alternatively, upload a resume through the dashboard.

---

## Start the Backend

```bash
cd backend
python -c "import uvicorn; uvicorn.run('app.main:app', host='127.0.0.1', port=8000)"
```

---

## Start the Frontend (Development)

```bash
cd frontend
pnpm dev
```

Dashboard: http://localhost:1420

---

## Start Legacy Flask Backend (Alternative)

```bash
python app.py
```

Dashboard: http://localhost:5000

---

# API Endpoints

| Method | Endpoint                    | Description                    |
| ------ | --------------------------- | ------------------------------ |
| GET    | /health                     | Health check                   |
| GET    | /api/dashboard/summary      | Dashboard funnel and activity  |
| GET    | /api/dashboard/stats        | Dashboard statistics           |
| GET    | /api/automation/config      | Get bot configuration          |
| PUT    | /api/automation/config      | Update bot configuration       |
| POST   | /api/automation/start       | Start automation bot           |
| POST   | /api/automation/pause       | Pause automation bot           |
| POST   | /api/automation/resume      | Resume automation bot          |
| POST   | /api/automation/stop        | Stop automation bot            |
| POST   | /api/automation/respond     | Answer a bot question          |
| GET    | /api/automation/status      | Get bot status                 |
| GET    | /api/automation/events      | Get automation event history   |
| GET    | /api/automation/events/stream | SSE event stream             |
| GET    | /api/saved-info/profile     | Get user profile               |
| PUT    | /api/saved-info/profile     | Update user profile            |
| GET    | /api/saved-info/keywords    | Get saved keywords             |
| PUT    | /api/saved-info/keywords    | Update saved keywords          |
| GET    | /api/saved-info/templates   | Get cover letter templates     |
| POST   | /api/saved-info/templates   | Create cover letter template   |
| DELETE | /api/saved-info/templates/{id} | Delete template             |
| GET    | /api/saved-info/resumes     | Get uploaded resumes           |
| POST   | /api/saved-info/resumes     | Upload resume                  |
| DELETE | /api/saved-info/resumes/{id} | Delete resume                |
| GET    | /api/analytics/applications | Application data by day        |
| GET    | /api/analytics/platforms    | Performance by platform        |
| GET    | /api/analytics/summary      | Analytics summary              |

---

# Usage Guide

## Step 1: Upload Resume

1. Upload a PDF, DOCX, or TXT resume
2. Parse the resume using AI
3. Review extracted information

## Step 2: Configure Settings

### Account Credentials

- LinkedIn Email
- LinkedIn Password
- Naukri Email
- Naukri Password

### Search Configuration

- Keywords
- Location
- Experience Level
- Job Type
- Remote Preference

### Application Controls

- Maximum Applications
- Dry Run Mode
- Blacklisted Companies
- Blacklisted Job Titles

## Step 3: Start Automation

1. Click **Start Bot**
2. Chrome launches automatically
3. Login is performed automatically
4. Solve CAPTCHA manually if prompted

## Step 4: Respond to Application Questions

If required information is missing, the system requests user input through the dashboard. Responses are automatically stored and reused.

## Step 5: Manage Saved Answers

The Saved Answers section allows users to view stored answers, delete individual entries, and clear all stored responses.

---

# Configuration

## constants.py

```python
BOT_SPEED = SPEED_SLOW
GROQ_MODEL = "llama-3.3-70b-versatile"
```

## Environment Variables

```bash
# Windows
set GROQ_API_KEY=your_api_key

# Linux / macOS
export GROQ_API_KEY=your_api_key
```

---

# Troubleshooting

## ChromeDriver Issues

- Ensure Google Chrome is installed
- Update Chrome to the latest version
- webdriver-manager automatically downloads compatible drivers

## LinkedIn Login Issues

- Verify credentials
- Complete CAPTCHA if requested
- Delete the cookies directory and retry
- Wait before retrying if LinkedIn temporarily blocks login attempts

## Naukri Login Issues

Naukri periodically updates its user interface. If login fails, check credentials, review generated debug screenshots, and update element selectors if required.

## Applications Are Not Being Submitted

- Resume parsing completed successfully
- Dry Run mode is disabled
- The target job supports automated application workflows

## Port Already in Use

```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Reset Application Data

```bash
# Windows
del user_answers.json
rmdir /s /q cookies
rmdir /s /q data
rmdir /s /q __pycache__
```

---

# Security Considerations

- User credentials are not persisted to disk
- Session cookies are stored locally
- AI API requests are only used for resume analysis
- Stored answers may contain personal information and should not be shared publicly

---

# Dependencies

## Python (Backend)

| Package             | Purpose                    |
| ------------------- | -------------------------- |
| fastapi             | Backend API framework      |
| uvicorn             | ASGI server                |
| sqlalchemy          | ORM for SQLite             |
| selenium            | Browser automation         |
| webdriver-manager   | ChromeDriver management    |
| selenium-stealth    | Automation detection mitigation |
| PyPDF2              | PDF resume parsing         |
| python-docx         | DOCX resume parsing        |
| python-multipart    | File upload support        |
| flask               | Legacy backend (compat)    |
| flask-cors          | CORS for legacy backend    |
| requests            | API communication          |
| cryptography        | Data encryption            |

## Node.js (Frontend)

| Package             | Purpose                    |
| ------------------- | -------------------------- |
| react               | UI framework               |
| vite                | Build tool                 |
| tailwindcss         | CSS framework              |
| recharts            | Charts and graphs          |
| lucide-react        | Icons                      |
| @radix-ui/*         | Accessible UI primitives   |

---

# License

This project is released under the MIT License. See the LICENSE file for details.