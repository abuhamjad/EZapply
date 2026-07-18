# EZApply — Modules

## Purpose

This document defines ownership and responsibility for each module in EZApply. It describes WHAT each module owns, not HOW it is implemented or used. 

Module boundaries are defined by Responsibility, not by directory layout. Each module owns specific concerns and must not reach into another module's concerns. Implementation details and workflows belong to other documents; this document is the single source of truth for module ownership.

## Table of Contents

- [Frontend Modules](#frontend-modules)
  - [Dashboard Module](#dashboard-module)
  - [Resume Module](#resume-module)
  - [Saved Information Module](#saved-information-module)
  - [Application Tracking Module](#application-tracking-module)
  - [Analytics Module](#analytics-module)
  - [Settings Module](#settings-module)
  - [Notifications Module](#notifications-module)
  - [Authentication Module](#authentication-module)
- [Backend Modules](#backend-modules)
  - [Automation Module](#automation-module)
  - [Platform Module](#platform-module)
  - [Learning Module](#learning-module)
- [Module Dependencies](#module-dependencies)
- [Communication Contract](#communication-contract)

## Frontend Modules

### Dashboard Module

**Responsibility**

Presents a unified summary of the user's job search: recent application activity, automation status, and headline metrics from other modules. Dashboard is read-oriented only; it aggregates and displays, it does not own any primary data.

**Owns**

- Dashboard UI layout and rendering.
- Aggregation of summary data from Application Tracking, Automation status, and Analytics modules.
- Navigation entry points into other feature modules.

**Depends On**

- Application Tracking Module (for recent applications and application count).
- Automation Module (for current automation status).
- Analytics Module (for headline metrics).

**Does NOT Own**

- Does not own application data or history — that is owned by Application Tracking Module.
- Does not own automation logic or control — that is owned by Automation Module.
- Does not own analytics computation — that is owned by Analytics Module.
- Does not make decisions about which data to display; it displays what features tell it to.

**Future Scope**

#### TODO

Dashboard enhancements and configurable widgets have not yet been designed.

**References**

- `FEATURES.md` — Dashboard
- `Architecture.md` — Module Architecture (Dashboard module)

### Resume Module

**Responsibility**

Manages all of the user's resumes: uploading, storing, organizing, and providing them to other modules that need resume content (automation, AI parsing).

**Owns**

- Resume file storage and retrieval.
- Resume version management (multiple versions, labeling, deletion).
- Resume metadata (upload date, selected version, etc.).

**Depends On**

- Persistence Layer (SQLite) for resume storage.
- No other modules.

**Does NOT Own**

- Does not parse resume content — that is owned by AI Resume Parsing (which calls into this module for resume files).
- Does not decide how resumes are used in applications — that is owned by Automation Module.
- Does not store extracted resume data — that is owned by Saved Information Module.

**Future Scope**

- Resume Optimization (see `PROJECT.md` — Future Scope).

**References**

- `FEATURES.md` — Resume Management, AI Resume Parsing
- `Architecture.md` — Module Architecture (Resume module)

### Saved Information Module

**Responsibility**

Stores the user's reusable information — personal details and screening question answers — so nothing ever has to be entered twice. This module is the single source of truth for what the user has told us about themselves.

**Owns**

- Personal detail storage (name, email, phone, address, etc.).
- Screening question answer storage.
- Information lifecycle (create, read, update, delete).
- Validation of stored information.

**Depends On**

- Persistence Layer (SQLite) for storage.
- No other modules.

**Does NOT Own**

- Does not extract information from resumes — that is owned by AI Resume Parsing (which populates this module).
- Does not decide what information to fill into applications — that is owned by Automation Module.
- Does not learn from application interactions — that is owned by Learning Module.

**Future Scope

#### TODO

Saved Information enhancements have not yet been designed.

**References**

- `FEATURES.md` — Saved Info, Question Learning System
- `Architecture.md` — Module Architecture (Saved Information module)

### Application Tracking Module

**Responsibility**

Records every job application the user makes (through automation or otherwise) and tracks its status over time. This module is the single source of truth for application history and outcomes.

**Owns**

- Application record creation and storage.
- Application status tracking and history.
- Application metadata (date applied, platform, role title, company, status, outcome, etc.).
- Query interface for listing and filtering applications.

**Depends On**

- Persistence Layer (SQLite) for application storage.
- Automation Module (notifies this module when an automation run completes).

**Does NOT Own**

- Does not compute analytics or insights from applications — that is owned by Analytics Module.
- Does not decide whether to apply to a job — that is owned by Automation Module.
- Does not parse job postings or match criteria — that is owned by Automation Module and Platform Module.

**Future Scope

#### TODO

Application Tracking enhancements have not yet been designed.

**References**

- `FEATURES.md` — Application Tracking
- `Architecture.md` — Module Architecture (Application Tracking module)

### Analytics Module

**Responsibility**

Transforms application data into insights about recruitment performance. Analytics is read-only with respect to application data; it queries but never modifies.

**Owns**

- Metrics computation (application count, outcome distribution, trends, etc.).
- Analytics query interface and data models.
- Visual presentation logic (chart data, aggregations).

**Depends On**

- Application Tracking Module (the source of all application data).

**Does NOT Own**

- Does not store applications — that is owned by Application Tracking Module.
- Does not decide what metrics to compute; it computes what is requested.
- Does not determine application success or failure — that is the responsibility of the user to record in Application Tracking.

**Future Scope**

- AI Career Insights (see `PROJECT.md` — Future Scope).

#### TODO

Analytics enhancements and new metrics have not yet been designed.

**References**

- `FEATURES.md` — Analytics
- `Architecture.md` — Module Architecture (Analytics module)

### Settings Module

**Responsibility**

Stores and provides user preferences and application configuration that affect how automation and the application behave. Settings persist across sessions.

**Owns**

- User preference storage (automation preferences, UI preferences, etc.).
- Application configuration (defaults, options, toggles).
- Settings persistence and retrieval.

**Depends On**

- Persistence Layer (SQLite) for settings storage.
- No other modules.

**Does NOT Own**

- Does not enforce how settings are used — that is the responsibility of the modules consuming the settings (Automation, etc.).
- Does not compute or infer settings values — the user sets them explicitly.

**Future Scope

#### TODO

The full catalog of settings and settings enhancements have not yet been designed.

**References**

- `FEATURES.md` — User Settings
- `Architecture.md` — Module Architecture (Settings module)

### Notifications Module

**Responsibility**

Delivers user-facing notifications about events that need attention: automation runs pausing for input, completing, or encountering errors.

**Owns**

- Notification creation and delivery.
- Notification lifecycle and status.
- Notification UI and presentation.

**Depends On**

- Automation Module (source of most notifications: pause for input, run complete, errors).

**Does NOT Own**

- Does not decide when to notify — that is the responsibility of the modules generating the events (Automation, etc.).
- Does not implement notification channels beyond in-app delivery (desktop native notifications, if supported, are application-level infrastructure).

**Future Scope

#### TODO

Notification channels and delivery mechanics have not yet been designed.

**References**

- `FEATURES.md` — Notifications
- `Architecture.md` — Module Architecture (Notifications module)

### Authentication Module

**Responsibility**

Establishes and maintains the user's identity within the application, protecting access to sensitive stored information.

**Owns**

- User identity (local profile or account, depending on the identity model).
- Identity verification.

**Depends On**

- Persistence Layer (SQLite) for storing identity data.
- No other modules.

**Does NOT Own**

- Does not authenticate to external platforms (LinkedIn, Indeed, etc.) — that is part of Session Management and Automation Module concerns.
- Does not manage authorization policies (which users can access which data) — that is single-user desktop context; authorization is implicit in authentication.

**Future Scope**

- Multi-device account support as part of cloud synchronization (see `Architecture.md` — Future Expansion).

#### TODO

Authentication requirements and model (local profile vs. account-based) have not yet been designed.

**References**

- `FEATURES.md` — Authentication
- `Architecture.md` — Module Architecture (Authentication module), Future Expansion
- `PROJECT.md` — Future Scope

## Backend Modules

### Automation Module

**Responsibility**

The core of EZApply: drives browser sessions against external job platforms, filling application forms with the user's information and resumes, and recording results in Application Tracking. The Automation Module is the only backend component that uses Playwright.

**Owns**

- Browser automation logic and session management.
- Platform-specific navigation and form-filling.
- Application form parsing and field detection.
- Pausing for user confirmation when input is required.
- Recording completed applications in Application Tracking.
- Respecting user automation preferences from Settings Module.
- Coordination with Learning Module for screening question detection.

**Depends On**

- Saved Information Module (personal details, screening answers).
- Resume Module (resume files).
- Application Tracking Module (records applications).
- Settings Module (automation preferences).
- Learning Module (detected question feedback).
- Platform Module (platform configuration and capabilities).
- Notifications Module (notifying the user).
- Authentication Module (if session/login state is needed).

**Does NOT Own**

- Does not expose Playwright or browser automation to the frontend (see `Architecture.md` — Architecture Constraints).
- Does not store resumes or personal details — that is owned by Resume Module and Saved Information Module.
- Does not decide which questions are screening questions — that is owned by Learning Module.
- Does not compute or display analytics — that is owned by Analytics Module.
- Does not own platform-specific configuration; platform definitions are owned by Platform Module.

**Future Scope

#### TODO

Automation enhancements and new capabilities have not yet been designed.

**References**

- `FEATURES.md` — Browser Automation
- `Architecture.md` — Module Architecture (Automation module), Layered Architecture (Automation Layer), Architecture Constraints

### Platform Module

**Responsibility**

Defines the external job platforms EZApply can automate and manages platform-specific configuration. Platform Module is the single source of truth for platform capabilities and requirements.

**Owns**

- Platform definitions (LinkedIn, Indeed, Naukri, etc.).
- Platform-specific capabilities and requirements.
- Per-platform user configuration and preferences.
- Platform metadata.

**Depends On**

- Persistence Layer (SQLite) for platform configuration storage.
- No other modules.

**Does NOT Own**

- Does not implement platform-specific automation logic — that is owned by Automation Module (which uses Platform Module definitions).
- Does not authenticate to platforms — that belongs to Authentication/Session Management (outside scope of current design).

**Future Scope**

- Support for additional platforms beyond LinkedIn, Indeed, and Naukri.
- A plugin system for platform extensibility (see `PROJECT.md` — Future Scope).

#### TODO

Per-platform capabilities, configuration, and the process for adding new platforms have not yet been designed.

**References**

- `FEATURES.md` — Platform Management
- `Architecture.md` — Module Architecture, Architectural Principles (Extensibility)
- `PROJECT.md` — Future Scope

### Learning Module

**Responsibility**

Builds and maintains the user's library of screening question answers by recognizing when questions appear in applications and prompting for answers, then saving them for reuse. Learning Module makes automation smarter over time without requiring the user to do anything but answer questions naturally.

**Owns**

- Question detection during automation runs.
- Question deduplication and matching logic.
- Learned question registry.
- Feedback from automation runs (which questions were asked, which were answered, which should be saved).

**Depends On**

- Saved Information Module (stores learned answers).
- Automation Module (detects questions during runs, provides feedback).

**Does NOT Own**

- Does not store answer content — that is owned by Saved Information Module.
- Does not decide whether to ask the user — that is owned by Automation Module via Bot Control.
- Does not decide which questions are "screening" vs. other types of questions (if such distinction exists); question classification belongs to Automation Module or future design work.

**Future Scope

#### TODO

Learning Module enhancements have not yet been designed.

**References**

- `FEATURES.md` — Question Learning System
- `Architecture.md` — Module Architecture (Automation, Saved Information modules)
- `docs/Roadmap.md` — v0.9 (Analytics & Learning System)

## Module Dependencies

```
Persistence Layer (SQLite)
  ^     ^     ^     ^      ^      ^
  |     |     |     |      |      |
  Resume  Saved Info  Application Tracking  Settings  Platform  Authentication
         Module      Module       Module     Module    Module     Module
  
         |           |              |          |
         +-----+-----+-----+--------+          |
               |           |                  |
         Automation Module <---+------+--------+
               |           |    |     |
               |    Learning Module   |
               |           |         |
         +-----+----------+--+       |
         |          |       |        |
    Application  Notifications   Dashboard
    Tracking       Module         Module
    Module           |             |
                     |      Analytics Module
                     |             |
                     +------+------+
```

## Communication Contract

All module communication across layers follows the architecture defined in `Architecture.md` — Communication Rules:

- The frontend calls the Backend Layer, which calls services (the Business Layer), which call the Persistence Layer and the Automation Layer.
- Modules do not call upward. Lower-layer modules never directly invoke upper-layer modules.
- Modules communicate with peers only through their defined public interfaces, never through internals.
- Data flows in one direction: from frontend → backend layers → persistence/automation.
- Responses flow back along the same path.

Per `Architecture.md`, the Persistence Layer is not exposed to the frontend. Frontend modules access data by calling Backend Layer services (routers), which access the Persistence Layer on their behalf.

Modules listed as "Depends On" above reference other modules at the business logic layer; implementation may bundle multiple modules into one router, service, or file, but the responsibility boundaries defined here remain.
