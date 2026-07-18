# EZApply — Version History

## Purpose

This document records every official version of EZApply and summarizes the major features, architectural improvements, and milestones introduced in each release.

Unlike the Development Log, this document tracks only official versioned releases and serves as the project's release history.

---

## Table of Contents

- [Versioning Scheme](#versioning-scheme)
- [Release Types](#release-types)
- [Version History](#version-history)
- [Upcoming Versions](#upcoming-versions)

---

# Versioning Scheme

EZApply follows **Semantic Versioning (SemVer)**.

```
MAJOR.MINOR.PATCH
```

Example:

```
v1.2.3
```

Where:

- **MAJOR** — Breaking architectural or user-facing changes.
- **MINOR** — Major development milestones and new functionality.
- **PATCH** — Bug fixes, maintenance, documentation updates, and minor improvements.

During active development, milestone versions (`v0.x.x`) represent major stages of the project's evolution.

---

# Release Types

| Type | Purpose |
|------|---------|
| Major | Significant architectural or product milestones. |
| Minor | New functionality or completed development phases. |
| Patch | Bug fixes, maintenance, documentation, or internal improvements. |

---

# Version History

---

## v0.1.0 — UI Foundation

**Release Status:** ✅ Released

### Objectives

- Establish the initial user interface.
- Implement the approved Figma design.
- Build the primary application pages.

### Included

- React + TypeScript application
- Tailwind CSS integration
- shadcn/ui integration
- Dashboard
- Bot Control
- Saved Information
- Analytics
- Desktop-oriented responsive layout
- Navigation system

### Notes

Established the visual foundation of EZApply using static placeholder data.

---

## v0.2.0 — Desktop Foundation

**Release Status:** ✅ Released

### Objectives

Convert the React application into a native desktop application.

### Included

- Tauri integration
- Rust project scaffold
- Native Windows desktop executable
- Desktop configuration
- React desktop integration
- Build system configuration

### Notes

Established the desktop application shell while keeping the frontend architecture unchanged.

---

## v0.3.0 — Project Blueprint

**Release Status:** ✅ Released

### Objectives

Complete the architectural planning before backend implementation.

### Included

- Complete software architecture
- Feature specifications
- Module ownership
- Workflow documentation
- Coding standards
- Architecture Decision Records (ADR)
- Development roadmap
- Current state documentation
- Version history
- Git strategy
- Documentation standards

### Notes

Established the architectural foundation that guides all future development.

---

## v0.4.0 — Frontend Foundation

**Release Status:** ✅ Released

### Objectives

Refactor the frontend into a scalable, maintainable architecture without changing the user experience.

### Included

- Modular frontend architecture
- Shared layout system
- Shared reusable component library
- Frontend service layer
- Custom React hooks
- Centralized TypeScript type system
- Shared mock data abstraction
- Frontend architecture audit
- Dead code cleanup
- Production build verification

### Notes

The frontend is now backend-ready. Future FastAPI integration will occur through the service layer without requiring structural changes to the UI.

---

## v0.5.0 — Backend Foundation

**Release Status:** ✅ Released

### Objectives

Create the backend architecture that will power the existing frontend without changing the frontend architecture.

### Included

- FastAPI project scaffold
- Backend folder structure
- Centralized configuration management
- Environment variable loading
- Centralized logging system
- SQLAlchemy engine, base, and session
- Dependency injection framework
- Centralized API router
- Health check endpoint
- Backend architecture audit
- Dead code cleanup

### Notes

The backend foundation is complete and fully integrated with the documented architecture. All infrastructure is production-ready and properly tested. The backend is ready for business logic and persistence layer implementation.

---

## v0.6.0 — Data & Persistence

**Release Status:** ✅ Released

### Objectives

Implement local persistent data storage using a SQLite database and SQLAlchemy.

### Included

- SQLite integration with automatic DB file creation.
- SQLAlchemy declarative base and ORM models (Profile, Resume, Template, Keyword, Run, Event, Application, Setting).
- Schema validation.
- EZApplyRepository pattern for secure and isolated database queries.
- Settings persistence and resume file path records.

### Notes

Replaced static frontend/backend configurations with persistent SQL rows.

---

## v0.7.0 — Frontend–Backend Integration

**Release Status:** ✅ Released

### Objectives

Integrate the frontend service layer with the FastAPI backend, removing mock data.

### Included

- Unified React Custom Hooks (`useDashboard`, `useAutomation`, `useSavedInfo`, `useAnalytics`) communicating with live services.
- API Client module wrapper using fetch with correct error response mapping.
- FastAPI backend routers mapping dashboard statistics, settings updates, keywords, profile information, and resume documents.
- Error validation and runtime response mapping (converting SQLAlchemy exceptions to HTTP 4xx/5xx).

### Notes

The application UI is now completely driven by FastAPI endpoints.

---

## v0.8.0 — Automation Engine

**Release Status:** ✅ Released

### Objectives

Integrate local selenium browser automation runners with real-time logging and events streamed to the user interface.

### Included

- Bot Control page hooks to start, pause, stop, and configure the runner.
- Daemon thread orchestration in the backend via `BotManager` and `LegacyBotService`.
- Server-Sent Events (SSE) events route enabling real-time streaming of automation console logs to the React UI terminal log viewer.
- Verification and manual/automatic redirection detection for platform (LinkedIn, Naukri) sign-ins.
- Driver factory module ensuring selenium launches appropriately on target Windows devices.

### Notes

EZApply is now fully integrated with the browser driver automation framework.

---

# Upcoming Versions

---

## v0.9.0 — Intelligence Layer

**Status:** 🔄 Next Release

### Planned Scope

- Resume text parsing and indexing.
- Machine learning/heuristic matching of form questions to profile data.
- AI suggestions and smart answer caching.
- Manual correction fallback form in the UI.

---

## v1.0.0 — Desktop MVP

**Status:** ⏳ Planned

### Planned Scope

- Complete desktop application distribution.
- Native installation packages (WIX/NSIS).
- Background auto-updater.
- Clean system tray integration.
- Production security review.

---

## Future Versions

Future releases may include:

- Mobile applications
- Cloud synchronization
- Multi-device synchronization
- Team collaboration
- Plugin system
- Enterprise features
- Additional AI-powered capabilities