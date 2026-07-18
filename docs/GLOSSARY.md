# EZApply — Glossary

## Purpose

This document defines the terminology used throughout EZApply.

It serves as the project's official vocabulary and should be referenced whenever technical or domain-specific terms appear in documentation or code.

Every contributor should use these definitions consistently to avoid ambiguity.

---

## Table of Contents

- [Domain Terms](#domain-terms)
- [Technical Terms](#technical-terms)
- [Abbreviations](#abbreviations)

---

# Domain Terms

## Application

A single job application submitted to an employer through a supported job platform.

---

## Applicant

The user of EZApply.

---

## Automation Run

A complete execution session of the automation engine, beginning when the user starts the bot and ending when it is stopped or completed.

---

## Bot

The browser automation engine responsible for performing repetitive job application tasks under user supervision.

---

## Bot Control

The user interface responsible for starting, pausing, resuming, monitoring, and stopping automation runs.

---

## Company Blacklist

A user-defined collection of companies that should never receive job applications.

---

## Easy Apply

A simplified application process provided by supported job platforms requiring minimal user interaction.

---

## Interview

A positive response from an employer requesting additional interaction with the applicant.

---

## Job Platform

A website or service used to search and apply for jobs.

Examples:

- LinkedIn
- Indeed
- Naukri

---

## Platform Session

An authenticated browser session for a supported job platform.

Sessions allow automation without requiring repeated logins.

---

## Resume

The primary document describing the applicant's education, skills, and experience.

---

## Resume Parsing

The process of extracting structured information from a resume.

---

## Saved Information

User-provided information stored locally for reuse during future applications.

Examples include:

- Personal details
- Education
- Work experience
- Skills
- Saved screening question answers

---

## Screening Question

A question presented during a job application requiring user input before submission.

---

## Question Learning

The process of storing previously answered screening questions so they can be reused in future applications.

---

## User Control Principle

The architectural principle stating that automation assists the user but never replaces user decision-making for unknown or irreversible actions.

---

# Technical Terms

## API

The communication interface between the frontend and backend.

EZApply uses FastAPI as its API layer.

---

## Business Logic

Application rules and decision-making processes independent of the user interface.

Business logic belongs exclusively to the backend.

---

## Feature Module

A self-contained functional area responsible for one business capability.

Examples:

- Dashboard
- Automation
- Resume
- Analytics

---

## Frontend

The React application responsible for presentation and user interaction.

---

## Backend

The FastAPI application responsible for business logic, automation, and persistence.

---

## Layered Architecture

The architectural pattern used throughout EZApply.

```
Frontend

↓

API Layer

↓

Service Layer

↓

Business Logic

↓

Persistence Layer
```

---

## Persistence Layer

The layer responsible for storing and retrieving application data.

---

## Service Layer

The layer responsible for coordinating business operations between the API and business logic.

---

## Shared Component

A reusable React component that can be used across multiple feature modules.

---

## Shared Utility

A reusable helper function or library that is not owned by a single feature module.

---

## Tauri

The desktop application shell that hosts the React frontend.

Tauri is responsible for native desktop integration only.

---

## Workflow

A documented sequence of interactions between the user and the system.

Workflows describe behavior rather than implementation.

---

## Module Ownership

The architectural principle that every feature is owned by exactly one module.

Ownership defines responsibility, not implementation.

---

## ADR (Architecture Decision Record)

A permanent record documenting why an important architectural decision was made.

---

# Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| ADR | Architecture Decision Record |
| API | Application Programming Interface |
| UI | User Interface |
| UX | User Experience |
| MVP | Minimum Viable Product |
| SPA | Single Page Application |
| CRUD | Create, Read, Update, Delete |
| DB | Database |
| ORM | Object Relational Mapping |
| SQL | Structured Query Language |
| JSON | JavaScript Object Notation |
| REST | Representational State Transfer |
| HTTP | Hypertext Transfer Protocol |
| HTTPS | Hypertext Transfer Protocol Secure |
| JWT | JSON Web Token |
| UUID | Universally Unique Identifier |
| CLI | Command Line Interface |
| IDE | Integrated Development Environment |
| CI | Continuous Integration |
| CD | Continuous Deployment |
| AI | Artificial Intelligence |
| LLM | Large Language Model |
| PDF | Portable Document Format |
| CSV | Comma-Separated Values |
| OCR | Optical Character Recognition |
| DOM | Document Object Model |
| SSR | Server-Side Rendering |
| CSR | Client-Side Rendering |
| TS | TypeScript |
| JS | JavaScript |
| CSS | Cascading Style Sheets |
| HTML | HyperText Markup Language |

---

## Glossary Maintenance

This glossary should be updated whenever:

- A new domain concept is introduced.
- A new architectural term becomes part of the project.
- New abbreviations are adopted.
- Existing terminology changes.

The goal is to maintain a single, consistent vocabulary across documentation, source code, and future development discussions.