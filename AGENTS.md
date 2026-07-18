# EZApply — Agent Instructions

## Purpose

This document defines the rules and working agreements for AI agents contributing to the EZApply codebase.

## Table of Contents

- [Project Context](#project-context)
- [Architecture Rules](#architecture-rules)
- [Working Rules](#working-rules)
- [Documentation Rules](#documentation-rules)
- [Documentation Duties](#documentation-duties)
- [Key Documents](#key-documents)

## Project Context

EZApply is an AI-powered desktop recruitment automation platform.

- Frontend: React + TypeScript + Tailwind CSS
- Desktop: Tauri
- Backend: FastAPI (Python)
- Automation: Playwright (Python)
- Database: SQLite (desktop version)

## Architecture Rules

1. UI is the source of truth. Never redesign the interface unless explicitly requested. Only connect data and functionality.
2. React never communicates directly with the database. All requests go through FastAPI.
3. All business logic belongs in the FastAPI backend.
4. Playwright is only used inside the backend. Never expose browser automation logic to React.
5. Every feature must be its own module. Avoid large files. Follow single-responsibility principles.
6. Never break existing functionality while adding features.
7. Prefer reusable components over duplicated code.
8. Use TypeScript everywhere in the frontend.
9. Use clean architecture and professional coding practices.
10. Keep the project organized and scalable.

## Working Rules

- Before making changes: explain what will change, list affected files, identify risks, then implement.
- Never modify unrelated code.
- If multiple approaches exist, recommend the most scalable one.

## Documentation Rules

- Documentation is the source of truth.
- Never overwrite existing documentation.
- Extend documentation instead of replacing it.
- If documentation conflicts with implementation, documentation wins until approved by the Product Owner.
- Every implementation must reference the appropriate documentation.
- Never implement undocumented features.
- Update documentation after implementation is complete.

## Documentation Update Policy

Documentation is updated only when a major version milestone is completed (e.g., v0.4.0, v0.5.0, v1.0.0).

Intermediate development milestones (v0.4.1, v0.4.2, etc.) should not trigger documentation updates unless they introduce a significant architectural decision or modify the project's design.

During milestone development:

- Commit code normally.
- Verify the application builds successfully.
- Keep documentation unchanged.

When the parent version is complete:

- Update CURRENT_STATE.md
- Update DEVELOPMENT_LOG.md
- Update ROADMAP.md
- Update VERSION_HISTORY.md

This keeps documentation concise, meaningful, and synchronized with stable project milestones rather than intermediate refactoring steps.

## Documentation Duties

### TODO

Define which documents agents must update after each change (e.g., `docs/DEVELOPMENT_LOG.md`, `docs/CURRENT_STATE.md`).

## Key Documents

- `docs/PROJECT.md` — project overview and goals
- `docs/Architecture.md` — master engineering guide and architecture rules
- `docs/Roadmap.md` — development roadmap
- `docs/VERSIONS.md` — version history
- `docs/CODING_STANDARDS.md` — coding conventions
- `docs/DECISIONS.md` — architecture decision records
- `docs/GLOSSARY.md` — domain and technical vocabulary
- `docs/FEATURES.md` — feature catalog and status
- `docs/WORKFLOWS.md` — user, system, and development workflows
- `docs/MODULES.md` — module responsibilities and boundaries
- `docs/DEVELOPMENT_LOG.md` — chronological development log
- `docs/CURRENT_STATE.md` — current project status
