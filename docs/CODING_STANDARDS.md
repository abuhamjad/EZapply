# EZApply — Coding Standards

## Purpose

This document defines the coding conventions, quality standards, and development practices used throughout the EZApply codebase. Every contributor, whether human or AI, must follow these standards to ensure consistency, maintainability, readability, and scalability.

---

## Table of Contents

- [General Principles](#general-principles)
- [Frontend Standards (React + TypeScript)](#frontend-standards-react--typescript)
- [Backend Standards (FastAPI +Python)](#backend-standards-fastapi--python)
- [Desktop Standards (Tauri)](#desktop-standards-tauri)
- [Naming Conventions](#naming-conventions)
- [File and Module Organization](#file-and-module-organization)
- [Comments and Documentation](#comments-and-documentation)
- [Error Handling](#error-handling)
- [Performance Guidelines](#performance-guidelines)
- [Security Guidelines](#security-guidelines)
- [Testing Standards](#testing-standards)

---

# General Principles

The following principles apply to every language and every layer of the project.

## Readability First

Code should be written for humans first and computers second.

Prefer simple, descriptive code over clever or overly compact implementations.

---

## Single Responsibility

Every function, component, service, and module should have one clearly defined responsibility.

Avoid mixing UI, business logic, and data access.

---

## DRY (Don't Repeat Yourself)

Duplicate logic should be extracted into reusable functions, hooks, utilities, or services.

---

## Keep Functions Small

Functions should perform one task.

Large functions should be split into smaller reusable functions.

---

## Avoid Hardcoded Values

Use constants, configuration files, or environment variables whenever possible.

---

## Explicit Over Implicit

Avoid hidden side effects.

Make dependencies obvious.

Prefer readable code over magic.

---

## Consistency

Follow existing patterns throughout the project.

Do not introduce new patterns unless they improve the overall architecture.

---

# Frontend Standards (React + TypeScript)

## Components

- One component per file.
- Components should remain focused on presentation.
- Avoid business logic inside components.
- Large pages should be composed of smaller components.

---

## State Management

- Keep state as local as possible.
- Avoid unnecessary global state.
- Derived state should not be stored.

---

## Services

Components should never communicate directly with the backend.

All communication must pass through the Service Layer.

---

## Hooks

Reusable logic should be extracted into custom hooks.

Hooks should never contain UI.

---

## Styling

- Tailwind CSS is the primary styling system.
- Do not use inline styles unless absolutely necessary.
- Reuse existing utility classes whenever possible.

---

## Props

Props should be strongly typed.

Avoid using `any`.

Interfaces should describe all public component APIs.

---

## TypeScript

- Enable strict typing.
- Prefer interfaces for public structures.
- Avoid `any`.
- Use enums only when appropriate.
- Prefer explicit return types for exported functions.

---

# Backend Standards (FastAPI + Python)

## Architecture

Follow layered architecture.

```
API Layer
↓

Service Layer
↓

Business Logic
↓

Persistence Layer
```

Each layer should communicate only with the layer directly below it.

---

## Routers

Routers should contain request handling only.

Business logic must never exist inside routers.

---

## Services

Services contain application logic.

Services should not directly manipulate UI or frontend concerns.

---

## Persistence

Database access belongs only in the Persistence Layer.

Business logic should never write SQL directly.

---

## Models

Use Pydantic models for API contracts.

Validate all external input.

---

## Python Style

Follow PEP 8.

Use type hints wherever possible.

Prefer descriptive names over abbreviations.

---

# Desktop Standards (Tauri)

- Tauri provides the desktop shell only.
- React owns the interface.
- FastAPI owns business logic.
- Rust should remain minimal.
- Avoid implementing business logic in Rust unless absolutely necessary.

---

# Naming Conventions

## Files

```
PascalCase.tsx
camelCase.ts
snake_case.py
```

---

## Components

Use PascalCase.

Example

```
DashboardCard
ResumeUploader
BotStatusPanel
```

---

## Functions

Use camelCase.

Examples

```
calculateStatistics()
loadResume()
startAutomation()
```

Python

```
calculate_statistics()
load_resume()
start_automation()
```

---

## Variables

Use descriptive names.

Avoid abbreviations unless universally understood.

---

## Constants

Use UPPER_SNAKE_CASE.

Example

```
DEFAULT_TIMEOUT
MAX_APPLICATIONS
```

---

## Boolean Variables

Begin with

```
is
has
can
should
```

Examples

```
isRunning
hasResume
canApply
shouldRetry
```

---

# File and Module Organization

Organize code by business modules rather than file type.

Example

```
modules/
    dashboard/
    analytics/
    automation/
    resume/
```

Shared code belongs inside

```
shared/
```

Infrastructure belongs inside

```
core/
```

Do not place unrelated functionality inside the same module.

---

# Comments and Documentation

Comments should explain **why**, not **what**.

Good comments explain reasoning, assumptions, or architectural decisions.

Avoid comments that simply restate the code.

Every exported function, class, and public API should have clear documentation where appropriate.

---

# Error Handling

Never silently ignore exceptions.

Handle expected failures gracefully.

Provide meaningful error messages.

Log unexpected failures.

Do not expose sensitive information in error messages.

---

# Performance Guidelines

Avoid premature optimization.

Optimize only after measuring.

Reuse expensive computations when appropriate.

Avoid unnecessary renders in React.

Avoid blocking operations in the UI thread.

---

# Security Guidelines

Never commit secrets.

Never hardcode credentials.

Validate all external input.

Escape or sanitize user-provided content when necessary.

Use environment variables for configuration.

---

# Testing Standards

Business logic should be testable independently of the UI.

Avoid tightly coupling components to implementation details.

Prefer deterministic code over code with hidden side effects.

Future automated tests should cover:

- Services
- Business logic
- Utilities
- Critical workflows

UI tests should focus on user behavior rather than implementation details.

---

## Coding Philosophy

Every line of code should contribute to one of the following goals:

- Readability
- Maintainability
- Scalability
- Reliability
- Simplicity

When multiple solutions are possible, choose the one that is easiest to understand and maintain.

Code is expected to evolve.

Write it so that future contributors can confidently extend it without rewriting existing functionality.