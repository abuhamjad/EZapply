# EZApply

**AI-Powered Job Application Automation System**

EZApply is an intelligent job application platform that automates the process of searching and applying for jobs on LinkedIn and Naukri.com. The system combines resume parsing, AI-assisted profile analysis, automated form filling, and browser automation to streamline the job application process.

---

## Overview

EZApply helps job seekers reduce repetitive manual work by automatically:

* Parsing resumes and extracting relevant information
* Generating job search keywords from candidate profiles
* Searching for relevant opportunities
* Completing application forms
* Managing user responses for recurring application questions
* Applying to jobs across multiple platforms

The system is designed as a full-stack application consisting of a Flask backend, browser automation services, AI-assisted resume analysis, and a web-based dashboard.

---

## Key Features

### Resume Parsing

* Upload resumes in PDF, DOCX, or TXT format
* Extract contact information automatically
* Identify skills, experience, education, and keywords
* Generate structured candidate profiles using AI

### Intelligent Job Search

* Generate job search keywords from resume data
* Search jobs based on skills and career profile
* Support multiple locations and experience levels
* Apply company and title blacklists

### Automated Job Applications

* LinkedIn Easy Apply automation
* Naukri.com job application automation
* Automatic resume upload
* Multi-step application handling

### Smart Form Filling

* Auto-fill common fields such as:

  * Name
  * Email
  * Phone number
  * Location
  * LinkedIn profile URL

### Interactive User Assistance

When application forms require information that cannot be extracted automatically, the system prompts the user for input through the dashboard.

Examples include:

* Notice period
* Current compensation
* Expected salary
* Work authorization status

### Persistent Answer Memory

* Stores user responses locally
* Reuses previously provided answers
* Eliminates repetitive form completion

### Session Persistence

* Saves authentication cookies
* Restores login sessions between runs
* Reduces repeated login requirements

## Project Structure

```text
EZApply/
│
├── app.py
├── bot_manager.py
├── linkedin_bot.py
├── naukri_bot.py
├── resume_parser.py
├── ai_matcher.py
├── constants.py
├── requirements.txt
├── README.md
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── resumes/
├── cookies/
├── data/
└── user_answers.json
```

### Core Modules

| File             | Description                          |
| ---------------- | ------------------------------------ |
| app.py           | Flask backend and API server         |
| bot_manager.py   | Coordinates bot execution and events |
| linkedin_bot.py  | LinkedIn automation logic            |
| naukri_bot.py    | Naukri automation logic              |
| resume_parser.py | Resume extraction and AI analysis    |
| ai_matcher.py    | Job matching and AI utilities        |
| constants.py     | Configuration values and defaults    |

---

## Auto-Generated Files

The following files and directories are created automatically during execution:

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

* Python 3.9 or later
* Google Chrome (latest version)
* Git
* Groq API Key (optional)

---

## Clone Repository

```bash
git clone https://github.com/your-username/EZApply.git
cd EZApply
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Add Resume

Place your resume inside the `resumes` directory.

```text
resumes/
└── Resume.pdf
```

Alternatively, upload a resume through the dashboard after starting the application.

---

## Start the Application

```bash
python app.py
```

Expected output:

```text
Job Apply Bot Server Starting...
Dashboard: http://localhost:5000
Put resumes in: ./resumes/
```

---

## Open Dashboard

Navigate to:

```text
http://localhost:5000
```

---

# Usage Guide

## Step 1: Upload Resume

1. Upload a PDF, DOCX, or TXT resume.
2. Parse the resume using AI.
3. Review extracted information.

---

## Step 2: Configure Settings

### Account Credentials

* LinkedIn Email
* LinkedIn Password
* Naukri Email
* Naukri Password

### AI Configuration

* Groq API Key (Optional)

### Search Configuration

* Keywords
* Location
* Experience Level
* Job Type
* Remote Preference

### Application Controls

* Maximum Applications
* Dry Run Mode
* Blacklisted Companies
* Blacklisted Job Titles

---

## Step 3: Start Automation

1. Click **Start Bot**
2. Chrome launches automatically
3. Login is performed automatically
4. Solve CAPTCHA manually if prompted

---

## Step 4: Respond to Application Questions

If required information is missing, the system requests user input through the dashboard.

Responses are automatically stored and reused in future sessions.

---

## Step 5: Manage Saved Answers

The Saved Answers section allows users to:

* View stored answers
* Delete individual entries
* Clear all stored responses

---

# Configuration

## constants.py

Important settings include:

```python
BOT_SPEED = SPEED_SLOW
GROQ_MODEL = "llama-3.3-70b-versatile"
```

These values can be modified to change runtime behavior.

---

## Environment Variables

Groq API credentials can be configured using environment variables.

Windows:

```bash
set GROQ_API_KEY=your_api_key

```

Linux / macOS:

```bash
export GROQ_API_KEY=your_api_key
```

---

# Troubleshooting

## ChromeDriver Issues

* Ensure Google Chrome is installed
* Update Chrome to the latest version
* webdriver-manager automatically downloads compatible drivers

---

## LinkedIn Login Issues

* Verify credentials
* Complete CAPTCHA if requested
* Delete the cookies directory and retry
* Wait before retrying if LinkedIn temporarily blocks login attempts

---

## Naukri Login Issues

Naukri periodically updates its user interface.

If login fails:

* Check credentials
* Review generated debug screenshots
* Update element selectors if required

---

## Applications Are Not Being Submitted

Verify that:

* Resume parsing completed successfully
* Dry Run mode is disabled
* The target job supports automated application workflows

---

## Port Already in Use

Windows:

```bash

netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Alternative:

```bash
python -c "from app import app; app.run(port=5001)"
```

---

## Reset Application Data

Windows:

```bash
del user_answers.json

rmdir /s /q cookies
rmdir /s /q data
rmdir /s /q __pycache__
```

---

# Security Considerations

* User credentials are not persisted to disk
* Session cookies are stored locally
* Groq API requests are only used for AI-assisted resume analysis
* Stored answers may contain personal information and should not be shared publicly

---

# Dependencies

| Package           | Purpose                         |
| ----------------- | ------------------------------- |
| Flask             | Backend API server              |
| Flask-CORS        | Cross-origin support            |
| Selenium          | Browser automation              |
| webdriver-manager | ChromeDriver management         |
| selenium-stealth  | Automation detection mitigation |
| PyPDF2            | PDF resume parsing              |
| python-docx       | DOCX resume parsing             |
| requests          | API communication               |

---

# Roadmap

### Planned Enhancements

* [ ] Advanced job quality scoring
* [ ] Skill gap analysis
* [ ] Resume tailoring for specific job descriptions
* [ ] Application history dashboard
* [ ] Email notifications
* [ ] Multiple resume profiles
* [ ] Additional job platform integrations
* [ ] Production deployment support













---

# License

This project is released under the MIT License.

See the LICENSE file for details.
