EZApply — AI-powered job application automation system
AI-powered job application bot that automatically applies to jobs on LinkedIn and Naukri.com using your resume.
![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-green?logo=flask)
![Selenium](https://img.shields.io/badge/Selenium-4.15+-orange?logo=selenium)
![License](https://img.shields.io/badge/License-MIT-yellow)
---
Features
Resume Parsing — Upload PDF/DOCX/TXT, AI extracts skills, keywords & contact info
Smart Job Search — Auto-searches jobs based on your resume skills
Auto Apply — Fills forms and applies to Easy Apply jobs automatically
Contact Auto-Fill — Phone, email, name, location filled from resume
Interactive Prompts — Bot asks YOU when it can't fill a field
Answer Memory — Saves your answers, never asks the same question twice
Cookie Persistence — Login sessions saved across restarts
---
Project Structure
```
Apply Bot/
├── app.py                 # Flask backend server (API routes)
├── bot\_manager.py         # Orchestrates bot threads \& events
├── linkedin\_bot.py        # LinkedIn Easy Apply automation
├── naukri\_bot.py          # Naukri.com job apply automation
├── resume\_parser.py       # AI + regex resume parsing
├── ai\_matcher.py          # Job-resume matching logic
├── constants.py           # URLs, config defaults, geo IDs
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── frontend/              # Dashboard UI
│   ├── index.html         # Main HTML page
│   ├── style.css          # Dark theme CSS
│   └── app.js             # Frontend logic (SSE, API calls)
│
├── resumes/               # Drop your resume here (auto-created)
├── cookies/               # Login session cookies (auto-created)
├── data/                  # Job tracking data (auto-created)
└── user\_answers.json      # Saved answers for form fields (auto-created)
```
Auto-Generated Files (safe to delete)
File	Purpose
`user\_answers.json`	Stores your answers to form questions so the bot doesn't ask again. Delete to reset.
`cookies/`	Saved login sessions for LinkedIn/Naukri. Delete to force re-login.
`data/`	Job application history and tracking.
`\_\_pycache\_\_/`	Python bytecode cache. Safe to delete anytime.
---
Quick Start
Prerequisites
Python 3.9+ — Download
Google Chrome — Download (latest version)
Groq API Key (optional) — Get free key for AI resume parsing
Step 1: Clone / Download
```bash
git clone <your-repo-url>
cd "Apply Bot"
```
Or download the ZIP and extract it.
Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
Step 3: Add Your Resume
Place your resume (PDF, DOCX, or TXT) in the `resumes/` folder:
```
resumes/
  └── Your\_Resume.pdf
```
> \*\*Or\*\* upload via the dashboard after starting the server.
Step 4: Start the Server
```bash
python app.py
```
You'll see:
```
Job Apply Bot Server Starting...
Dashboard: http://localhost:5000
Put resumes in: ./resumes/
```
Step 5: Open Dashboard
Open your browser and go to:
```
http://localhost:5000
```
---
Usage Guide
1. Upload & Parse Resume
Drag & drop your resume onto the upload area (or click to browse)
Click "Parse AI" to extract skills, keywords, and contact info
Verify the extracted contact info (phone, email, location) is correct
2. Configure Settings
Setting	Description
Platforms	Toggle LinkedIn and/or Naukri
LinkedIn Email/Password	Your LinkedIn login credentials
Naukri Email/Password	Your Naukri login credentials
Groq API Key	(Optional) For smarter AI resume parsing
Search Keywords	Auto-filled from resume, or type your own
Location	Job search location (default: India)
Experience Level	Internship, Entry, Mid-Senior, etc.
Max Applications	Limit per session (default: 50)
Mode	Live Apply or Dry Run (test without applying)
Blacklist Companies	Skip specific companies
3. Start the Bot
Click "▶ Start Bot"
Chrome will open automatically and log into LinkedIn/Naukri
If CAPTCHA appears, solve it manually (bot waits 30 seconds)
4. Interactive Prompts
When the bot encounters a form field it can't fill:
A pulsing cyan prompt appears in the Live Activity feed
Type your answer and press Enter or click Send
Click Skip to leave the field empty
Your answer is saved permanently — bot won't ask again
5. Saved Answers
Scroll down to the "Saved Answers" card to see all stored Q&A pairs:
Click the X button to delete a specific answer
Click the trash icon in the header to clear all answers
Answers persist in `user\_answers.json` across sessions
---
Configuration File Reference
`constants.py`
Edit this file to change default URLs, speed, and presets:
```python
BOT\_SPEED = SPEED\_SLOW    # Change to SPEED\_FAST or SPEED\_MEDIUM
GROQ\_MODEL = "llama-3.3-70b-versatile"  # Change AI model
```
Environment Variables (optional)
```bash
# Set Groq API key as env variable instead of UI input
set GROQ\_API\_KEY=gsk\_your\_key\_here
```
---
Troubleshooting
"ChromeDriver not found"
Make sure Google Chrome is installed and up to date
`webdriver-manager` auto-downloads the correct driver
"LinkedIn login failed"
Double-check email/password
Solve CAPTCHA manually if it appears (bot waits 30s)
Delete `cookies/` folder and retry
LinkedIn may temporarily block automated logins — wait and retry
"Naukri login error: no such element"
Naukri changes their UI frequently
The bot uses 8+ fallback selectors — if all fail, check if Naukri updated their login page
A debug screenshot is saved as `naukri\_login\_debug.png`
Bot skips jobs / doesn't apply
Ensure resume is parsed (click "Parse AI")
Check "Dry Run" mode is OFF (set to "Live Apply")
Some jobs require additional steps the bot can't handle
Port 5000 already in use
```bash
# Kill existing process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use a different port
python -c "from app import app; app.run(port=5001)"
```
Reset everything
```bash
# Delete all saved data
del user\_answers.json
rmdir /s /q cookies
rmdir /s /q data
rmdir /s /q \_\_pycache\_\_
```
---
Security Notes
Credentials are NOT stored on disk — they stay in browser memory only
Login cookies are saved locally in `cookies/` for session persistence
Groq API key is only sent to Groq's servers for resume parsing
`user\_answers.json` may contain personal info — don't share publicly
---
Dependencies
Package	Purpose
`flask`	Web server & API
`flask-cors`	Cross-origin requests
`selenium`	Browser automation
`webdriver-manager`	Auto ChromeDriver management
`selenium-stealth`	Anti-bot detection bypass
`PyPDF2`	PDF resume parsing
`python-docx`	DOCX resume parsing
`requests`	HTTP calls to Groq API
---
Roadmap
[ ] Naukri.com form auto-fill (like LinkedIn)
[ ] Job application history page
[ ] Email notifications on completion
[ ] Multiple resume profiles
[ ] Production deployment with Gunicorn
---
License
MIT License — free to use, modify, and distribute.
---
