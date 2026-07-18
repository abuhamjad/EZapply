# EZApply — Architecture Decision Records

## Purpose

This document records significant architectural and technical decisions made throughout the development of EZApply.

The purpose of an Architecture Decision Record (ADR) is to explain **why** a decision was made, not simply **what** was implemented.

Once a decision is accepted, it becomes part of the project's architectural history and should only be superseded by a newer ADR.

---

## Table of Contents

- [Decision Record Format](#decision-record-format)
- [Decision Status](#decision-status)
- [Architecture Decision Records](#architecture-decision-records)

---

# Decision Record Format

Each decision follows the format below.

```markdown
### ADR-XXX: Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded

#### Context

Why the decision was required.

#### Decision

What was decided.

#### Consequences

Benefits, trade-offs, and long-term implications.
```

---

# Decision Status

| Status | Meaning |
|---------|---------|
| Proposed | Under discussion and not yet finalized. |
| Accepted | Official project decision. |
| Superseded | Replaced by a newer ADR. |

---

# Architecture Decision Records

---

## ADR-001 — Feature-Based Frontend Architecture

- **Date:** 2026-07
- **Status:** Accepted

### Context

The project is expected to grow significantly over time. Organizing the frontend by file type would become difficult to maintain as the number of features increases.

### Decision

The frontend will follow a feature-based architecture where each business module owns its components, hooks, services, and types.

Example:

```
modules/
    dashboard/
    analytics/
    automation/
    resume/
```

Shared functionality will exist outside feature modules.

### Consequences

**Advantages**

- Clear ownership.
- Better scalability.
- Easier maintenance.
- Simpler onboarding.

**Trade-offs**

- Slightly deeper folder hierarchy.
- Requires discipline when creating new modules.

---

## ADR-002 — Layered Backend Architecture

- **Date:** 2026-07
- **Status:** Accepted

### Context

Business logic, persistence, and API endpoints should remain independent to simplify testing and future maintenance.

### Decision

The backend follows a layered architecture:

```
API
↓

Service

↓

Business Logic

↓

Persistence
```

Each layer communicates only with the layer directly below it.

### Consequences

**Advantages**

- Easier testing.
- Better separation of concerns.
- Improved maintainability.

**Trade-offs**

- More project structure.
- Slight increase in boilerplate.

---

## ADR-003 — React as the Single UI Layer

- **Date:** 2026-07
- **Status:** Accepted

### Context

The project originally explored multiple desktop UI technologies.

### Decision

React is the only user interface framework used across the project.

The same React codebase should support desktop today and mobile in the future wherever practical.

### Consequences

**Advantages**

- One UI codebase.
- Faster development.
- Easier maintenance.

**Trade-offs**

- Requires a desktop shell (Tauri).
- Mobile support may require platform-specific adaptations.

---

## ADR-004 — Tauri for Desktop

- **Date:** 2026-07
- **Status:** Accepted

### Context

The project required a desktop application while keeping resource usage low.

### Decision

Tauri is used as the desktop shell.

Rust remains minimal and only provides desktop integration.

Business logic remains in Python.

### Consequences

**Advantages**

- Lightweight executable.
- Native desktop experience.
- Smaller memory footprint.

**Trade-offs**

- Introduces Rust into the project.
- Desktop-specific APIs require Tauri integration.

---

## ADR-005 — FastAPI as Backend

- **Date:** 2026-07
- **Status:** Accepted

### Context

The application requires a backend that is modular, asynchronous, and easy to extend.

### Decision

FastAPI will provide all backend functionality.

The frontend communicates only through FastAPI.

### Consequences

**Advantages**

- High performance.
- Strong typing.
- Automatic API documentation.
- Easy testing.

**Trade-offs**

- Additional API layer between UI and business logic.

---

## ADR-006 — Backend Owns Business Logic

- **Date:** 2026-07
- **Status:** Accepted

### Context

Mixing business logic into the frontend creates duplication and makes future platform support difficult.

### Decision

React is responsible only for presentation.

All business logic belongs to the backend.

### Consequences

**Advantages**

- Single source of truth.
- Easier debugging.
- Future mobile support.

**Trade-offs**

- Requires API communication for all operations.

---

## ADR-007 — Browser Automation Lives in the Backend

- **Date:** 2026-07
- **Status:** Accepted

### Context

Browser automation must operate independently of the user interface.

### Decision

Playwright will execute entirely within the backend.

The frontend only starts, stops, monitors, and configures automation.

### Consequences

**Advantages**

- Better separation of concerns.
- Easier testing.
- Independent automation engine.

**Trade-offs**

- Progress updates require communication with the frontend.

---

## ADR-008 — Documentation Before Implementation

- **Date:** 2026-07
- **Status:** Accepted

### Context

The project is intended to be developed over a long period with assistance from multiple AI coding agents.

### Decision

Core architecture and documentation are completed before backend implementation begins.

Documentation serves as the primary source of truth.

### Consequences

**Advantages**

- Reduced ambiguity.
- Better planning.
- Easier collaboration.
- Consistent AI-generated code.

**Trade-offs**

- Higher initial planning effort.
- Slower start to implementation.

---

## ADR-009 — User Control Principle

- **Date:** 2026-07
- **Status:** Accepted

### Context

Automation should assist the user without making irreversible decisions independently.

### Decision

The user always remains in control.

The system may automate repetitive tasks but must pause whenever manual input or confirmation is required.

### Consequences

**Advantages**

- Increased trust.
- Better transparency.
- Safer automation.

**Trade-offs**

- Slightly slower automation in exceptional cases.

---

## ADR-010 — Modular Development Workflow

- **Date:** 2026-07
- **Status:** Accepted

### Context

Large refactors are difficult to review, test, and maintain.

### Decision

Development proceeds through small, versioned milestones.

Each milestone is independently planned, implemented, reviewed, committed, and documented before moving to the next.

### Consequences

**Advantages**

- Easier debugging.
- Smaller code reviews.
- Stable Git history.
- Better rollback capability.

**Trade-offs**

- More frequent commits.
- More planning required.

---

## Future Decisions

Future ADRs should document decisions involving:

- Database architecture
- Synchronization strategy
- Mobile architecture
- AI integrations
- Plugin system
- Cloud services
- Authentication model
- Deployment strategy
- Update mechanism
- Multi-user support