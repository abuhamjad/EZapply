# EZApply — Project Overview

> **Version:** v0.3 - Blueprint  
> **Status:** In Progress  
> **Primary Platform:** Desktop (Windows)  
> **Future Platforms:** Android & iOS

## Purpose

This document defines what EZApply is, why it exists, and the goals that guide its development.

## Table of Contents

- [Project Summary](#project-summary)
- [Mission Statement](#mission-statement)
- [Vision](#vision)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Target Users](#target-users)
- [Success Criteria](#success-criteria)
- [Core Principles](#core-principles)
- [Technology Stack](#technology-stack)
- [Project Scope](#project-scope)
- [Current Status](#current-status)
- [Development Philosophy](#development-philosophy)
- [Repository Structure](#repository-structure)
- [Version Roadmap](#version-roadmap)
- [Future Vision](#future-vision)
- [Related Documents](#related-documents)

## Project Summary

EZApply is an AI-powered desktop recruitment automation platform that automates job applications.

EZApply is an AI-powered desktop application that streamlines the complete job application workflow.

The application allows users to upload and manage resumes, extract structured information, configure automation preferences, automate repetitive job applications, store reusable answers, monitor application progress, and analyze recruitment performance through a unified dashboard.

The application follows a desktop-first philosophy while maintaining an architecture that allows future expansion to mobile platforms without redesigning the backend.

## Mission Statement

EZApply is a desktop-first AI recruitment assistant designed to automate repetitive job application tasks while keeping users in complete control of their job search. The platform combines resume intelligence, browser automation, application analytics, and reusable user information into a single professional desktop application.

## Vision

Our vision is to build an intelligent, reliable, and extensible recruitment assistant that simplifies the job application process without removing user control. EZApply aims to become a productivity tool that helps candidates spend less time filling repetitive forms and more time preparing for interviews and advancing their careers.

## Problem Statement

Job seekers repeatedly perform the same tasks across multiple recruitment platforms.

Common challenges include:

- Re-entering personal information
- Uploading resumes repeatedly
- Answering identical screening questions
- Searching multiple job platforms
- Tracking application status manually
- Managing several resume versions
- No centralized analytics
- Time-consuming application process

These repetitive tasks reduce productivity and make job searching frustrating.

## Solution

EZApply centralizes the entire recruitment process into a single desktop application.

The system provides:

- Resume Intelligence
- Intelligent profile management
- Browser automation
- Reusable answer management
- Application tracking
- Automation controls
- Recruitment analytics
- Persistent user preferences

The goal is to eliminate repetitive work while allowing the user to remain in complete control of every automation process.

## Goals

### TODO

List the primary goals of the project.

## Non-Goals

### TODO

List what EZApply intentionally does not attempt to do.

## Target Users

### Primary Users

- Students
- Fresh Graduates
- Entry-Level Developers
- Internship Applicants

### Secondary Users

- Experienced Professionals
- Career Switchers
- Freelancers
- Remote Job Seekers

### Future Users

- Universities
- Placement Cells
- Career Consultants
- Recruitment Agencies

## Success Criteria

### TODO

Define measurable criteria for project success.

## Core Principles

### Desktop First

The desktop application is the primary platform.

All features are designed for the desktop experience before expanding to mobile platforms.

### User Control

Automation should never remove user control.

Whenever user input is required, the system pauses and requests confirmation rather than making assumptions.

### Documentation First

Architecture is designed before implementation.

Documentation serves as the source of truth for the project.

### Modular Design

Every feature belongs to a dedicated module.

Modules communicate through clearly defined interfaces.

### Maintainability

The project should remain understandable months or years after development.

Readable code and documentation are prioritized over quick implementations.

### Extensibility

The architecture should support future features without requiring major redesigns.

## Technology Stack

### Frontend

- React
- TypeScript
- Tailwind CSS
- shadcn/ui

### Desktop

- Tauri
- Rust

### Backend

- FastAPI
- Python

### Automation

- Playwright

### Database

- SQLite

### AI

- LLM APIs
- Resume Parsing
- NLP

## Project Scope

### Current Scope

- Desktop Application
- Resume Management
- Browser Automation
- Application Tracking
- Analytics Dashboard
- Saved Information
- Bot Control

### Future Scope

- Android Application
- iOS Application
- Cloud Synchronization
- Multi-device Support
- AI Career Insights
- Resume Optimization
- Plugin System

## Current Status

### Current Version

v0.3 — Blueprint

### Completed

- ✅ UI Foundation
- ✅ Desktop Foundation (Tauri)
- ✅ Initial Documentation Structure

### Current Sprint

Project Architecture & Documentation

### Next Sprint

Frontend Architecture

## Development Philosophy

The project follows a documentation-first development process.

Every feature progresses through the following lifecycle:

Idea

↓

Architecture

↓

Documentation

↓

Implementation

↓

Testing

↓

Review

↓

Merge

↓

Documentation Update

Implementation never precedes architecture.

## Repository Structure

```
EZApply/
│
├── frontend/        React + TypeScript + Tailwind
├── backend/         FastAPI (Python)
├── desktop/         Tauri Desktop Shell
├── docs/            Project Documentation
├── shared/          Shared Models & Types
└── assets/          Static Assets
```

## Version Roadmap

The complete roadmap is maintained in **Roadmap.md**.

Current Progress:

- v0.1 — UI Foundation ✅
- v0.2 — Desktop Foundation ✅
- v0.3 — Blueprint 🚧
- v0.4 — Frontend Architecture
- v0.5 — Backend Foundation
- v0.6 — Database Foundation
- v0.7 — Resume Intelligence
- v0.8 — Automation Engine
- v0.9 — Analytics & Learning System
- v1.0 — Desktop MVP

## Future Vision

EZApply is designed as more than a final-year project.

The long-term vision is to evolve into a complete AI-powered career platform that combines intelligent resume management, browser automation, recruitment analytics, and personalized career assistance while maintaining a modular architecture and desktop-first philosophy.

Future mobile applications will reuse the same backend architecture to provide a consistent user experience across devices.

## Related Documents

- Architecture.md
- Features.md
- Modules.md
- Workflows.md
- Roadmap.md
- AGENTS.md
