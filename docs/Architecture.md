# EZApply Master Engineering Guide

## Table of Contents

- [Project Overview](#project-overview)
- [Current Tech Stack](#current-tech-stack)
- [Project Goal](#project-goal)
- [Architecture Rules](#architecture-rules)
- [Folder Structure](#folder-structure)
- [Coding Style](#coding-style)
- [Response Style](#response-style)
- [System Overview](#system-overview)
- [Architectural Principles](#architectural-principles)
- [High-Level System Architecture](#high-level-system-architecture)
- [Layered Architecture](#layered-architecture)
- [Module Architecture](#module-architecture)
- [Communication Rules](#communication-rules)
- [Repository Structure](#repository-structure)
- [Dependency Rules](#dependency-rules)
- [Future Expansion](#future-expansion)
- [Architecture Constraints](#architecture-constraints)

## Project Overview

EZApply is an AI-powered desktop recruitment automation platform.

## Current Tech Stack

- Frontend: React + TypeScript + Tailwind CSS
- Desktop: Tauri
- Backend: FastAPI (Python)
- Automation: Playwright (Python)
- Database: SQLite (Desktop Version)
- Mobile: React Native (Future Phase)

## Project Goal

Build a professional, production-quality desktop application that automates job
applications while keeping the architecture modular, maintainable, and scalable.
The desktop version is the primary target. Mobile support will be added later
using the same backend.

## Architecture Rules

Never break these rules:

1. UI is the source of truth.
   - Never redesign the interface unless explicitly requested.
   - Preserve the existing React + Tailwind UI.
   - Only connect data and functionality.
2. React never communicates directly with the database.
   - All requests must go through FastAPI.
3. All business logic belongs in the FastAPI backend.
   - React should only display data and send user actions.
4. Playwright is only used inside the backend.
   - Never expose browser automation logic to React.
5. Every feature must be its own module.
   - Avoid large files.
   - Follow single-responsibility principles.
6. Never break existing functionality while adding features.
7. Prefer reusable components over duplicated code.
8. Use TypeScript everywhere in the frontend.
9. Use clean architecture and professional coding practices.
10. Keep the project organized and scalable.

## Folder Structure

```text
EZApply/
|-- frontend/
|-- backend/
|-- desktop/
|-- docs/
`-- shared/
```

## Coding Style

- Keep code readable.
- Add comments only when they improve understanding.
- Use descriptive variable names.
- Avoid hardcoded values.
- Keep functions small and focused.
- Prefer composition over duplication.

## Response Style

Before making changes:

1. Explain what will be changed.
2. List the affected files.
3. Identify any risks.
4. Then implement the solution.

Never modify unrelated code.

If multiple approaches exist, recommend the most scalable one.

## System Overview

EZApply is structured as a desktop application composed of three cooperating runtimes:

1. A **Tauri desktop shell** (Rust) that hosts the application window and provides operating-system integration.
2. A **React frontend** (TypeScript + Tailwind CSS) that renders the entire user interface inside the Tauri webview.
3. A **FastAPI backend** (Python) that owns all business logic, persistence (SQLite), and browser automation (Playwright).

The frontend never contains business logic and never touches the database or the automation engine directly. Every meaningful operation — parsing a resume, launching an automation run, recording an application — is a request from the frontend to the backend. The backend is the single authority for state and behavior; the frontend is a view over that authority.

This separation exists so that the backend can later serve other clients (mobile applications, cloud services) without modification, and so that each part of the system can be reasoned about, tested, and replaced independently.

### Desktop-First Philosophy

The desktop application is the primary platform. Every feature is designed, documented, and implemented for the desktop experience first.

Desktop-first has concrete architectural consequences:

- The backend runs locally alongside the desktop shell; no network infrastructure is required to use the product.
- SQLite is the persistence layer because it is embedded, zero-configuration, and suited to a single-user local application.
- Browser automation runs on the user's own machine, under the user's observation and control, consistent with the User Control principle.
- The backend API is designed as if it were remote (clean HTTP boundaries, no frontend-specific coupling) so that future mobile and cloud phases can reuse it without redesign.

## Architectural Principles

### Separation of Concerns

Each part of the system has exactly one area of responsibility. The frontend renders and collects input. The backend decides and executes. The database stores. The automation engine drives browsers. No layer performs another layer's job, and no concern is spread across layers.

### Single Responsibility

Every module, file, and function should have one reason to change. Features live in dedicated modules rather than shared catch-all files. Large files are a signal that responsibilities need to be split.

### Documentation First

Architecture is designed and documented before implementation begins. Documentation is the source of truth: when documentation and implementation conflict, documentation wins until the Product Owner approves a change. Undocumented features are not implemented.

### Desktop First

The desktop application is the primary target. Features are not compromised or generalized prematurely for hypothetical platforms; instead, the backend boundary is kept clean so future platforms can reuse it.

### Extensibility

The architecture must support future features — mobile applications, cloud synchronization, plugins — without major redesign. This is achieved by keeping module boundaries explicit, communication paths narrow, and the backend independent of any particular client.

### Maintainability

The project must remain understandable months or years after development. Readable code, small focused modules, and up-to-date documentation are prioritized over quick implementations.

## High-Level System Architecture

The system consists of the Tauri shell, the React frontend it hosts, and the FastAPI backend the frontend communicates with. The backend owns SQLite and Playwright.

```text
+---------------------------------------------------------------+
|                     Tauri Desktop Shell (Rust)                |
|                                                               |
|   +-------------------------------------------------------+   |
|   |            React Frontend (TypeScript)               |   |
|   |            UI rendering + user input only             |   |
|   +---------------------------+---------------------------+   |
|                               |                               |
+-------------------------------|-------------------------------+
                                | HTTP (local API requests)
                                v
+---------------------------------------------------------------+
|                    FastAPI Backend (Python)                   |
|                                                               |
|   Routers  -->  Services (business logic)                     |
|                     |                    |                    |
|                     v                    v                    |
|              +-------------+     +----------------+           |
|              |   SQLite    |     |   Playwright   |           |
|              | (database)  |     |  (automation)  |           |
|              +-------------+     +--------+-------+           |
|                                           |                   |
+-------------------------------------------|-------------------+
                                            v
                                  External job platforms
                                  (browser sessions)
```

Roles of each technology:

- **Tauri** provides the native window, application lifecycle, packaging, and operating-system integration. It hosts the React frontend in a webview.
- **React** implements the entire user interface. It displays data and sends user actions to the backend. It holds no business logic.
- **FastAPI** exposes the API the frontend consumes and contains all business logic. It is the only component permitted to access the database and the automation engine.
- **SQLite** is the embedded local database. It is accessed exclusively by the backend's persistence layer.
- **Playwright** performs browser automation against external job platforms. It runs exclusively inside the backend and is never exposed to the frontend.

### TODO

- Define how the backend process is launched and supervised by the desktop shell (startup, shutdown, crash recovery).
- Define the local API transport details (port selection, security of the local endpoint).

## Layered Architecture

The system is organized into layers with strictly defined responsibilities. Each layer may only communicate with its adjacent layers, as defined in [Communication Rules](#communication-rules).

### Desktop Layer

The Tauri shell. Responsible for the application window, native menus, operating-system integration, packaging, and application lifecycle. It hosts the Presentation Layer and has no knowledge of business logic or data.

### Presentation Layer

The React component tree: pages, layouts, and reusable UI components. Responsible for rendering state and capturing user input. It contains no business logic, no persistence, and no direct API calls — data access is delegated to the Frontend Service Layer.

### Frontend Service Layer

The frontend's API client layer. Responsible for communicating with the FastAPI backend: composing requests, handling responses and errors, and exposing typed functions the Presentation Layer calls. This is the only frontend code that talks to the backend.

### Backend Layer

The FastAPI routers. Responsible for exposing HTTP endpoints, validating incoming requests, and translating them into calls to the Business Layer. Routers contain no business logic themselves.

### Business Layer

The backend services. Responsible for all business logic: rules, decisions, orchestration of persistence and automation, and enforcement of user-control checkpoints. This is the only layer allowed to invoke the Persistence Layer and the Automation Layer.

### Persistence Layer

The database access code around SQLite. Responsible for storing and retrieving data. It exposes data operations to the Business Layer and contains no business rules.

### Automation Layer

The Playwright-based automation engine. Responsible for driving browser sessions against external job platforms. It is invoked only by the Business Layer, and it never communicates with the frontend directly.

### TODO

- Define the internal structure of the Business Layer (service granularity, shared service utilities).
- Define the Persistence Layer approach (ORM vs. query layer, migration strategy).

## Module Architecture

Every feature is a dedicated module. A module spans the layers it needs — typically a frontend page plus service client, a backend router plus service, and its persistence — but its boundaries are explicit and it communicates with other modules only through defined interfaces.

The major system modules are:

### Dashboard

The unified home view. Presents an overview of the user's job search: application activity, automation status, and key metrics surfaced from other modules.

### Resume

Resume management and resume intelligence. Covers uploading and managing resume versions and extracting structured information from resumes.

### Automation

The browser automation engine and its controls. Covers configuring automation preferences, running automated job applications via Playwright, and pausing for user confirmation whenever input is required.

### Analytics

Recruitment analytics. Aggregates application data into insights about recruitment performance.

### Settings

User preferences and application configuration. Covers persistent user preferences and automation controls.

### Saved Information

Reusable user information. Stores personal details and reusable answers to screening questions so they never have to be re-entered.

### Application Tracking

Application progress monitoring. Records applications and their statuses across platforms.

### Authentication

User identity within the application.

#### TODO

Authentication requirements for the local desktop version (local profile vs. account-based) have not yet been designed.

### Notifications

User-facing notifications for events that require attention, such as automation runs pausing for input or completing.

#### TODO

Notification channels and delivery mechanics (in-app, desktop-native) have not yet been designed.

Detailed module responsibilities and boundaries are maintained in `MODULES.md`.

## Communication Rules

Data flows through the system along a single, strictly ordered path:

```text
Desktop Layer
    |
Presentation Layer  (React components)
    |
Frontend Service Layer  (API client)
    |            ^
    | HTTP       | HTTP responses
    v            |
Backend Layer  (FastAPI routers)
    |
Business Layer  (services)
    |                     |
Persistence Layer     Automation Layer
   (SQLite)            (Playwright)
```

Allowed communication:

- The **Presentation Layer** may call only the **Frontend Service Layer**.
- The **Frontend Service Layer** may call only the **Backend Layer**, over HTTP.
- The **Backend Layer** may call only the **Business Layer**.
- The **Business Layer** may call the **Persistence Layer** and the **Automation Layer**.
- Responses flow back along the same path in reverse.

Forbidden communication:

- The frontend never communicates with the database. All requests go through FastAPI.
- The frontend never communicates with the Automation Layer. Browser automation is never exposed to React.
- Routers never bypass services to reach the database or the automation engine.
- The Persistence Layer and the Automation Layer never call upward into the layers above them.
- Modules never reach into another module's internals; they interact only through that module's defined interface.

### TODO

- Define how long-running automation runs report progress back to the frontend (polling vs. push) — this decision has not yet been made.

## Repository Structure

```text
EZApply/
|-- frontend/    React + TypeScript + Tailwind CSS application.
|                All Presentation Layer and Frontend Service Layer code.
|-- backend/     FastAPI (Python) application.
|                All routers, services, persistence, and Playwright automation.
|-- desktop/     Tauri desktop shell (Rust).
|                Window management, packaging, OS integration.
|-- docs/        Project documentation — the source of truth for the project.
|-- shared/      Shared models, types, and contracts used across layers.
`-- assets/      Static assets.
```

Folder purposes:

- **frontend/** contains everything that runs in the Tauri webview. It depends on the backend API contract, never on backend internals.
- **backend/** contains everything that runs in the Python process: the API surface, business logic, database access, and automation. It has no knowledge of the frontend.
- **desktop/** contains the Tauri shell configuration and Rust code. It hosts the frontend and integrates with the operating system.
- **docs/** contains all project documentation. Documentation is written before implementation and updated after it.
- **shared/** contains contracts shared between layers, such as data models and types.
- **assets/** contains static assets used by the application.

### TODO

- Define the internal folder layout of `frontend/` and `backend/` (per-module organization) when the Frontend Architecture and Backend Foundation phases are designed.
- Define the exact contents and format of `shared/` (how contracts are shared between TypeScript and Python).

## Dependency Rules

Dependencies point in one direction: from the user-facing layers toward the backend, and inside the backend from the API surface toward business logic, persistence, and automation. Lower layers never depend on higher layers.

Allowed dependencies:

| Component | May depend on |
| --- | --- |
| Desktop Layer (Tauri) | Presentation Layer (hosts it) |
| Presentation Layer | Frontend Service Layer, shared types |
| Frontend Service Layer | Backend API contract, shared types |
| Backend Layer (routers) | Business Layer, shared models |
| Business Layer (services) | Persistence Layer, Automation Layer, shared models |
| Persistence Layer | SQLite only |
| Automation Layer | Playwright only |

Forbidden dependencies:

- Frontend code must never depend on backend internals, the database, or Playwright.
- The Presentation Layer must never depend on HTTP details; only the Frontend Service Layer does.
- Routers must never depend on the Persistence Layer or the Automation Layer directly.
- The Persistence Layer must never depend on services, routers, or automation.
- The Automation Layer must never depend on routers or the frontend.
- No module may depend on another module's internals — only on its defined interface.
- `shared/` must never depend on `frontend/`, `backend/`, or `desktop/`; the dependency always points toward `shared/`.

## Future Expansion

### Future Mobile Applications

Mobile support (Android and iOS) is a planned future phase. The architecture supports it as follows:

- All business logic, persistence, and automation live behind the FastAPI backend. A mobile application is another client of the same API.
- The frontend never holds business logic, so no logic needs to be ported or duplicated for mobile.
- The Frontend Service Layer pattern is reproducible on mobile: a mobile client layer calls the same backend endpoints.

#### TODO

Where the backend runs in the mobile scenario (on-device, on the user's desktop, or in the cloud) has not yet been designed.

### Future Cloud Synchronization

Cloud synchronization and multi-device support are planned future phases. The architecture keeps them possible:

- The Persistence Layer is isolated behind the Business Layer, so the storage strategy can evolve without touching the frontend or the API surface.
- The backend API is designed as if remote, so introducing a cloud-hosted counterpart does not require redesigning client communication.

#### TODO

Synchronization model, conflict resolution, account model, and data privacy design have not yet been designed.

## Architecture Constraints

These rules are permanent. The architecture will never violate them:

1. The UI is the source of truth. The interface is never redesigned unless explicitly requested; only data and functionality are connected.
2. React never communicates directly with the database. All requests go through FastAPI.
3. All business logic belongs in the FastAPI backend. React only displays data and sends user actions.
4. Playwright is used only inside the backend. Browser automation logic is never exposed to React.
5. Every feature is its own module with single responsibility. Large catch-all files are not permitted.
6. Existing functionality is never broken by new features.
7. Automation never removes user control. When user input is required, the system pauses and requests confirmation rather than making assumptions.
8. Documentation is the source of truth. It is extended, never overwritten, and implementation never precedes architecture.
9. TypeScript is used everywhere in the frontend.
10. Dependencies flow in one direction only, as defined in [Dependency Rules](#dependency-rules); lower layers never depend on higher layers.
