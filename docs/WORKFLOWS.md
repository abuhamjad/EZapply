# EZApply — Workflows

## Purpose

This document describes the key workflows in EZApply: the sequences of interactions between users and the system over time. This document answers "what happens next?" — it describes HOW the system responds to user actions and how components coordinate.

Workflows are organized into three categories:

- **User Workflows** — initiated by the user, visible in the UI.
- **System Workflows** — internal sequences, often triggered by user actions but orchestrated by the backend.
- **Development Workflows** — how to build, test, and deploy EZApply.

Each workflow is defined at the conceptual level. For implementation details, see `Architecture.md`, `MODULES.md`, and `FEATURES.md`.

## Table of Contents

- [User Workflows](#user-workflows)
  - [First-Time Setup](#first-time-setup)
  - [Resume Upload & Parsing](#resume-upload--parsing)
  - [Configure Settings](#configure-settings)
  - [Start Bot & Run Automation](#start-bot--run-automation)
  - [Application Shutdown](#application-shutdown)
- [System Workflows](#system-workflows)
  - [Automated Job Application](#automated-job-application)
  - [Screening Question Detection](#screening-question-detection)
  - [Application Tracking Update](#application-tracking-update)
  - [Analytics Computation](#analytics-computation)
  - [Platform Session Management](#platform-session-management)
- [Development Workflows](#development-workflows)

## User Workflows

### First-Time Setup

**Purpose**

Initialize EZApply for first use: establish the user's identity and capture initial personal information.

**Trigger**

User launches EZApply for the first time.

**Preconditions**

- EZApply is installed and running.
- The user has not yet been authenticated or profiled in this instance.

**Main Flow**

1. The system detects first-time launch (no user profile exists).
2. The system presents the setup flow.
3. The user completes authentication (see Platform Session Management workflow).
4. The user is prompted to enter or upload personal information (name, email, phone, etc.).
5. The system stores the user's profile in Saved Information (see MODULES.md — Saved Information Module).
6. The user optionally uploads resumes during setup (see Resume Upload & Parsing workflow).
7. Setup completes and the Dashboard is displayed.

**Alternate Flows**

#### Resuming Interrupted Setup

If the user exits during setup:
- The system saves progress and offers to resume on next launch.
- The user can complete setup or skip to the Dashboard.

#### TODO

Alternative authentication methods (if account-based authentication is designed) have not yet been specified.

**Failure Handling**

- If personal information validation fails, the system presents an error and returns to the affected step.
- If profile storage fails, the system presents an error and offers to retry.

**Result**

The user is authenticated and has a complete profile. The system is ready for job applications.

**References**

- `FEATURES.md` — Authentication, Saved Info
- `MODULES.md` — Authentication Module, Saved Information Module
- Platform Session Management workflow

### Resume Upload & Parsing

**Purpose**

Let the user upload resumes and extract structured information automatically using AI Resume Parsing (see `FEATURES.md` — AI Resume Parsing).

**Trigger**

User initiates resume upload, either during First-Time Setup or later through Resume Management (see `FEATURES.md` — Resume Management).

**Preconditions**

- User is authenticated.
- The user has a resume file to upload.

**Main Flow**

1. The user selects a resume file to upload.
2. The system validates the file (format, size, etc.).
3. The system stores the resume file (Resume Module, see MODULES.md).
4. The system extracts structured information from the resume using AI Resume Parsing.
5. The system presents the extracted information to the user for review and correction.
6. The user reviews the extraction and approves, rejects, or corrects individual fields.
7. Approved information is stored in Saved Information (Saved Information Module, see MODULES.md).
8. The resume is now available for use in automation runs.

**Alternate Flows**

#### Manual Information Entry

If the user rejects the extraction:
- The user manually enters the information instead.
- The system stores the user's entries in Saved Information.

#### Multiple Resume Versions

If the user uploads multiple resumes:
- Each resume is stored as a separate version.
- The user can mark one as "default" or select which resume to use per automation run.

#### TODO

Supported resume formats have not yet been designed.

**Failure Handling**

- If file upload fails, the system presents an error and allows retry.
- If AI extraction fails, the system offers the user a choice: retry extraction, or manually enter information.
- If information storage fails, the system presents an error and allows retry.

**Result**

The resume is uploaded and stored. Extracted information has been approved by the user and is now available in Saved Information. The resume is available for automation runs.

**References**

- `FEATURES.md` — Resume Management, AI Resume Parsing, Saved Info
- `MODULES.md` — Resume Module, Saved Information Module

### Configure Settings

**Purpose**

Allow the user to configure automation preferences and application settings.

**Trigger**

User navigates to Settings.

**Preconditions**

- User is authenticated.

**Main Flow**

1. The user navigates to the Settings view.
2. The system presents all available settings categories (automation preferences, UI preferences, etc.).
3. The user adjusts one or more settings.
4. The user saves the changes.
5. The system validates the settings.
6. The system stores the updated settings (Settings Module, see MODULES.md).
7. The system applies the new settings immediately (no restart required).
8. Settings confirmation is displayed.

**Alternate Flows**

#### Reset to Defaults

If the user chooses to reset:
- The system presents a confirmation dialog.
- If confirmed, the system resets all settings to defaults and saves.

#### TODO

The catalog of available settings has not yet been designed.

**Failure Handling**

- If settings validation fails, the system presents an error and highlights the invalid setting.
- If settings storage fails, the system presents an error and offers retry.

**Result**

Settings are updated and persist across sessions. Affected features (e.g., Automation Module) immediately use the new settings.

**References**

- `FEATURES.md` — User Settings
- `MODULES.md` — Settings Module

### Start Bot & Run Automation

**Purpose**

Initiate an automated job application run and let the user supervise it.

**Trigger**

User clicks "Start Bot" or "Run Automation" in Bot Control (see `FEATURES.md` — Bot Control).

**Preconditions**

- User is authenticated.
- User has saved personal information in Saved Information.
- User has configured automation preferences in Settings.
- User has uploaded at least one resume.
- Resumes and Saved Information contain complete required fields (per Settings preferences).

**Main Flow**

1. The user initiates a run from Bot Control.
2. The system validates preconditions; if any are missing, the system notifies the user and returns.
3. The system starts the automation run in the backend (see Automated Job Application workflow).
4. The system displays the live automation status and progress.
5. The user watches the automation execute and can pause or stop at any time.
6. During execution, if automation pauses for user confirmation (see Screening Question Detection workflow), Bot Control displays the pause and input request.
7. The user responds or continues.
8. Automation completes (success, pause, or failure).
9. The system records the run result.
10. The system displays the run summary and next steps.

**Alternate Flows**

#### Pause During Run

If the user clicks "Pause":
- Automation pauses at the next safe point.
- The user can resume or stop.

#### Stop During Run

If the user clicks "Stop":
- Automation stops and rolls back any uncommitted changes.
- The run is recorded as incomplete.

#### TODO

Job selection and filtering (which jobs to apply to) have not yet been designed.

**Failure Handling**

- If automation encounters a platform error, the system pauses, logs the error, and notifies the user (see Notifications Module, MODULES.md).
- If a form field cannot be filled (missing required data), the system pauses and requests confirmation (see Screening Question Detection workflow).
- If the run fails catastrophically, the system stops, records the failure, and presents an error summary.

**Result**

One or more job applications have been submitted. Results are recorded in Application Tracking (see Application Tracking Update workflow). The user can review results on the Dashboard or in Application Tracking.

**References**

- `FEATURES.md` — Bot Control, Browser Automation, Saved Info, Resume Management
- `MODULES.md` — Automation Module, Saved Information Module, Resume Module, Settings Module, Notifications Module
- Automated Job Application workflow
- Screening Question Detection workflow

### Application Shutdown

**Purpose**

Cleanly shut down the application.

**Trigger**

User closes the application window or selects "Exit".

**Preconditions**

- The application is running.

**Main Flow**

1. The user initiates shutdown.
2. The system checks for in-progress automation.
3. If automation is running, the system displays a confirmation dialog (stop the automation?).
4. If the user confirms, automation is stopped and results are saved.
5. The system persists any unsaved state (settings, pending updates).
6. The system closes all resources cleanly.
7. The desktop shell (Tauri) closes the application window.
8. The application exits.

**Alternate Flows**

#### Cancel Shutdown

If the user clicks "Cancel" on the confirmation dialog:
- The application remains open.
- Automation continues.

#### Background Shutdown

If the user wants the automation to continue while the window is closed:

#### TODO

Whether the application can run in the background (without a visible window) has not yet been designed.

**Failure Handling**

- If automation cannot be stopped cleanly, the system presents an error and offers forced shutdown.
- If state persistence fails, the system logs the error, offers retry, and allows shutdown to proceed (state may be lost).

**Result**

The application is closed. All state is persisted. The next launch will resume with the saved state.

**References**

- `Architecture.md` — Layered Architecture (Desktop Layer)

## System Workflows

### Automated Job Application

**Purpose**

Core system workflow: the sequence of steps the backend Automation Module executes to apply to a single job.

**Trigger**

User starts Bot via the Start Bot workflow. The Automation Module receives a job target and user preferences.

**Preconditions**

- User has authenticated.
- User has saved personal information.
- User has uploaded resumes.
- Job posting URL or job ID is available (from user, job search, or job queue).

**Main Flow**

1. Automation Module receives a job posting URL/ID.
2. Automation Module opens a browser session to the job platform (see Platform Session Management workflow).
3. Automation Module navigates to the job posting.
4. Automation Module parses the application form (field detection, field types, required vs. optional).
5. For each form field:
   a. Automation Module attempts to fill the field with data from Saved Information or Resumes (Resume Module, Saved Information Module).
   b. If no matching data exists, Automation Module pauses (see Screening Question Detection workflow).
   c. If a value was saved from previous applications (Question Learning System, see MODULES.md — Learning Module), Automation Module uses it.
   d. If the user confirms the field value, the field is filled.
6. Automation Module submits the application form.
7. The platform responds (success, error, or redirection).
8. Automation Module records the application in Application Tracking (see Application Tracking Update workflow).
9. The result is returned to the user via Bot Control.

**Alternate Flows**

#### Platform Requires Account Login

If the platform requires authentication:
- Automation Module checks browser session (see Platform Session Management workflow).
- If not authenticated, Automation Module pauses and notifies the user (see Notifications Module, MODULES.md).

#### Multi-Step Application

If the application process has multiple pages:
- Automation Module treats each page as a separate step in the main flow above.

#### TODO

Job search and selection (which jobs to apply to) have not yet been designed.

**Failure Handling**

- If form parsing fails, Automation Module pauses with details.
- If form submission fails, Automation Module retries once, then pauses if the retry fails.
- If the platform returns an error (e.g., "Application already submitted"), Automation Module records the outcome and continues.

**Result**

The application has been submitted (or skipped). The outcome is recorded in Application Tracking.

**References**

- `FEATURES.md` — Browser Automation
- `MODULES.md` — Automation Module, Saved Information Module, Resume Module, Learning Module
- Screening Question Detection workflow
- Application Tracking Update workflow
- Platform Session Management workflow

### Screening Question Detection

**Purpose**

Detect when an automation run encounters a form field that requires user input, pause the run, and request the answer from the user.

**Trigger**

During Automated Job Application workflow, Automation Module encounters a form field without a pre-filled value or a saved answer.

**Preconditions**

- Automation is running and has reached a form field that needs a value.
- No saved answer is available in Saved Information for this field.

**Main Flow**

1. Automation Module detects a form field requiring input (e.g., a screening question like "Why do you want this job?").
2. Automation Module checks Learning Module for a saved answer to this question.
3. If a saved answer exists, Automation Module uses it (see Alternate Flow: Learned Question).
4. If no saved answer exists, Automation Module pauses the automation run.
5. Automation Module sends a notification to the user (see Notifications Module, MODULES.md).
6. The system displays the question and context in Bot Control and requests user input.
7. The user types an answer in the UI.
8. The user clicks "Continue" or "Skip This Field".
9. If "Continue": the answer is sent to Automation Module, which fills the field and continues the run.
10. If "Skip This Field": the field is left blank (if optional) or the application is skipped (if required).
11. The answer is stored in Saved Information and registered with Learning Module for future reuse.
12. The automation run resumes.

**Alternate Flows**

#### Learned Question

If Learning Module has a saved answer for this question:
- Automation Module displays the saved answer to the user for review.
- The user can accept the saved answer (continue) or provide a new answer (edit).
- If edited, the new answer is saved.

#### Ambiguous Question

If Automation Module cannot determine whether a field is a screening question (e.g., an open text field with unclear purpose):

#### TODO

Question classification and matching logic have not yet been designed.

**Failure Handling**

- If the user does not respond within a timeout, Automation Module displays a reminder notification.
- If the application is required to be completed but the user skips all fields, Automation Module skips this job.

**Result**

The user has answered the question, the answer is saved for future reuse, and the automation run resumes or continues to the next job.

**References**

- `FEATURES.md` — Question Learning System, Bot Control
- `MODULES.md` — Learning Module, Saved Information Module, Notifications Module, Automation Module

### Application Tracking Update

**Purpose**

Record the outcome of each job application in the system's persistent record.

**Trigger**

Automation Module completes an application submission (successful, failed, or skipped) in the Automated Job Application workflow.

**Preconditions**

- A job application has been attempted by Automation Module.
- Application Tracking Module is ready to accept records.

**Main Flow**

1. Automation Module prepares an application record (job URL, company, role title, application date/time, status, outcome).
2. Automation Module sends the record to Application Tracking Module.
3. Application Tracking Module validates the record.
4. Application Tracking Module stores the record in persistence (Persistence Layer, see `Architecture.md`).
5. Application Tracking Module notifies Dashboard and Analytics modules that new data is available.
6. The application count on the Dashboard is updated.
7. On next Analytics refresh (see Analytics Computation workflow), the new application is included.

**Alternate Flows**

#### User Manual Entry

If the user wants to record an application made outside EZApply:

#### TODO

Whether users can manually record external applications has not yet been designed.

**Failure Handling**

- If validation fails, Application Tracking Module rejects the record and notifies Automation Module of the error.
- If storage fails, Application Tracking Module retries, and if the retry fails, notifies the user via Notifications Module.

**Result**

The application is recorded in Application Tracking and visible in the Dashboard and Analytics.

**References**

- `FEATURES.md` — Application Tracking
- `MODULES.md` — Application Tracking Module
- Automated Job Application workflow
- Analytics Computation workflow

### Analytics Computation

**Purpose**

Compute recruitment metrics and insights from application data whenever new applications are recorded or the user requests a refresh.

**Trigger**

1. A new application is recorded (triggered by Application Tracking Update workflow).
2. User manually refreshes Analytics from the Dashboard or Analytics view.
3. The application starts and loads Analytics data (daily or weekly, depending on preferences).

**Preconditions**

- Application Tracking contains at least one recorded application.

**Main Flow**

1. Analytics Module receives a computation request.
2. Analytics Module queries Application Tracking Module for all applications.
3. Analytics Module computes metrics (application count, outcome distribution, applications per day/week, etc.).
4. Analytics Module prepares visualization data (chart data, summaries, trends).
5. Analytics Module caches the results (to avoid re-computation on every view).
6. The Dashboard is notified of updated headline metrics.
7. The Analytics view displays the full metrics and visualizations.

**Alternate Flows**

#### Filtered Analytics

If the user filters Analytics (by date range, platform, status, etc.):
- Analytics Module recomputes for the filtered subset.
- Results are displayed immediately.

#### TODO

Specific metrics and visualization types have not yet been designed.

**Failure Handling**

- If querying Application Tracking fails, Analytics Module displays a "data unavailable" state and offers retry.
- If computation fails, Analytics Module displays an error and offers retry.

**Result**

Metrics are computed and cached. Dashboard displays headline metrics. Analytics view displays full metrics and visualizations.

**References**

- `FEATURES.md` — Analytics
- `MODULES.md` — Analytics Module, Application Tracking Module
- Application Tracking Update workflow

### Platform Session Management

**Purpose**

Manage browser sessions with external job platforms so that the user does not have to log in to each platform for every automation run.

**Trigger**

Automation Module needs to interact with an external job platform (LinkedIn, Indeed, Naukri, etc.) in Automated Job Application workflow.

**Preconditions**

- The user has valid credentials for the target platform (stored securely, pending authentication design).
- The user has configured platform access in Platform Management (see `FEATURES.md` — Platform Management).

**Main Flow**

1. Automation Module requests a browser session to the target platform from Platform Session Management.
2. Platform Session Management checks if a valid session already exists in browser cache.
3. If a valid session exists, Platform Session Management returns the session handle and continues to Automated Job Application.
4. If no session exists:
   a. Platform Session Management opens a new browser instance.
   b. Platform Session Management navigates to the platform's login page.
   c. Platform Session Management attempts to authenticate using stored credentials (pending design of authentication mechanism).
   d. If authentication succeeds, Platform Session Management caches the session.
   e. If authentication fails, Platform Session Management notifies the user via Notifications Module and pauses (see Screening Question Detection workflow).
5. Automation Module uses the session to navigate to the job posting (see Automated Job Application).
6. At the end of the run or when the session is no longer needed, Platform Session Management maintains the session for reuse on the next run.

**Alternate Flows**

#### Session Expired

If a cached session becomes invalid (user logged out, cookies expired):
- Platform Session Management detects the invalid state during next use.
- Platform Session Management clears the session and attempts re-authentication.

#### TODO

Credential storage and retrieval mechanism have not yet been designed.

**Failure Handling**

- If authentication fails, Platform Session Management notifies the user and pauses.
- If the platform redirects unexpectedly, Platform Session Management logs the redirect and pauses with details.

**Result**

A valid browser session with the target platform is established. Automation Module can proceed with application submission.

**References**

- `FEATURES.md` — Platform Management
- `MODULES.md` — Platform Module
- `Architecture.md` — Architecture Constraints
- Automated Job Application workflow

## Development Workflows

### TODO

Development workflows (running the application locally, building the desktop bundle, testing, deployment, release process) have not yet been designed. See `docs/DEVELOPMENT_LOG.md` for current development notes.
