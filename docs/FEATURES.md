# EZApply — Features

## Purpose

This document catalogs the features of EZApply, their status, and their specifications. It describes WHAT each feature does from the user's perspective. Architecture, module boundaries, and workflows are owned by `Architecture.md`, `MODULES.md`, and `WORKFLOWS.md`.

## Table of Contents

- [Feature Status Legend](#feature-status-legend)
- [Dashboard](#dashboard)
- [Bot Control](#bot-control)
- [Saved Info](#saved-info)
- [Analytics](#analytics)
- [Resume Management](#resume-management)
- [Browser Automation](#browser-automation)
- [Application Tracking](#application-tracking)
- [User Settings](#user-settings)
- [Notifications](#notifications)
- [Authentication](#authentication)
- [Session Management](#session-management)
- [Search & Filtering](#search--filtering)
- [AI Resume Parsing](#ai-resume-parsing)
- [Question Learning System](#question-learning-system)
- [Platform Management](#platform-management)
- [Planned Features](#planned-features)

## Feature Status Legend

- **Planned** — specified but not started
- **In Progress** — under active development
- **Implemented** — complete and working
- **Deferred** — postponed to a later phase

All features cataloged below are currently **Planned**. Workflows are not yet documented; per-feature workflow references will be added once `WORKFLOWS.md` is written.

## Dashboard

### Purpose

The home screen of EZApply: a single, read-oriented overview of the user's job search, drawing on recent application activity, automation status, and headline metrics, with navigation into the other features.

### Capabilities

- Display a summary of recent application activity.
- Display the current automation status (see [Bot Control](#bot-control)).
- Display headline metrics from [Analytics](#analytics).
- Provide navigation entry points into the other features.

### Future Scope

#### TODO

Dashboard-specific enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Dashboard module)

## Bot Control

### Purpose

The user's command center for [Browser Automation](#browser-automation), enforcing the User Control principle (`PROJECT.md` — Core Principles): the user starts, pauses, resumes, and stops automation, and the system pauses to ask for confirmation rather than making assumptions.

### Capabilities

- Start, pause, resume, and stop automation runs.
- Display the live status of the current automation run.
- Pause automation and request user confirmation whenever input is required.
- Let the user respond to confirmation requests and resume the run.

### Future Scope

#### TODO

Bot Control enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Automation module), Architecture Constraints
- `PROJECT.md` — Core Principles (User Control)

## Saved Info

### Purpose

The user's store of reusable information — personal details and reusable answers to screening questions — so nothing ever has to be entered twice. Saved information fills application forms during automation runs, and the user can view, edit, and delete everything stored.

### Capabilities

- Store and manage personal details used in application forms.
- Store and manage reusable answers to screening questions.
- Allow the user to view, edit, and delete any saved information.
- Supply saved information to automation runs.

### Future Scope

#### TODO

Saved Info enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Saved Information module)
- `PROJECT.md` — Problem Statement

## Analytics

### Purpose

Aggregates application data into insights about recruitment performance. Where [Application Tracking](#application-tracking) records individual applications, Analytics answers the bigger questions: how many applications, over what time, with what outcomes.

### Capabilities

- Aggregate application data into recruitment metrics.
- Present metrics visually in a dedicated analytics view.
- Feed headline metrics to the [Dashboard](#dashboard).

#### TODO

The specific metrics and visualizations have not yet been designed.

### Future Scope

- AI Career Insights (see `PROJECT.md` — Future Scope).

### References

- `Architecture.md` — Module Architecture (Analytics module)
- `PROJECT.md` — Problem Statement

## Resume Management

### Purpose

One organized place for all of the user's resumes: upload once, keep multiple versions, and reuse them across applications. Uploaded resumes are the input for [AI Resume Parsing](#ai-resume-parsing) and for automation runs that require a resume file.

### Capabilities

- Upload resume files into the application.
- Store and manage multiple resume versions.
- Allow the user to view, organize, and delete resume versions.
- Provide resumes to automation runs and to AI Resume Parsing.

### Future Scope

- Resume Optimization (see `PROJECT.md` — Future Scope).

### References

- `Architecture.md` — Module Architecture (Resume module)
- `PROJECT.md` — Problem Statement

## Browser Automation

### Purpose

The core of EZApply: applies to jobs on the user's behalf by driving real browser sessions against external job platforms, filling forms with the user's [Saved Info](#saved-info) and resumes, and recording results in [Application Tracking](#application-tracking). The user directs and supervises every run through [Bot Control](#bot-control) — the automation is an assistant that does the typing, not a black box.

### Capabilities

- Run automated job applications on supported platforms (see [Platform Management](#platform-management)).
- Fill application forms using saved personal details, reusable answers, and resumes.
- Pause and request user confirmation whenever input is required.
- Record each application's outcome in Application Tracking.
- Respect the user's automation preferences from [User Settings](#user-settings).

### Future Scope

#### TODO

Automation enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Automation module), Architecture Constraints
- `PROJECT.md` — Mission Statement, Core Principles (User Control)

## Application Tracking

### Purpose

The user's single record of every job application and its status over time — one place to answer "where did I apply, and what happened?" — replacing manual tracking. It is the data source for [Analytics](#analytics).

### Capabilities

- Record applications made through the automation.
- Track the status of each application.
- Let the user browse and review their application history.
- Provide application data to Analytics and the Dashboard.

#### TODO

Whether users can record applications made outside EZApply manually has not yet been designed.

### Future Scope

#### TODO

Application Tracking enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Application Tracking module)
- `PROJECT.md` — Problem Statement

## User Settings

### Purpose

Where the user configures the application: automation preferences that govern [Browser Automation](#browser-automation) behavior, and application-level preferences. All settings persist across sessions.

### Capabilities

- Configure automation preferences.
- Configure application preferences.
- Persist all settings across sessions.

#### TODO

The full catalog of settings has not yet been designed.

### Future Scope

#### TODO

Settings enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Settings module)
- `PROJECT.md` — Solution (persistent user preferences)

## Notifications

### Purpose

Informs the user about events that need their attention — an automation run pausing for confirmation, completing, or failing — so the system can pause and ask without the user having to watch constantly.

### Capabilities

- Notify the user when automation pauses for confirmation.
- Notify the user when automation runs complete or fail.

#### TODO

Notification channels and delivery mechanics (in-app, desktop-native) have not yet been designed.

### Future Scope

#### TODO

Notification enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Notifications module)

## Authentication

### Purpose

Establishes the user's identity within the application and protects their stored information (personal details, resumes, application history).

### Capabilities

#### TODO

Authentication requirements for the local desktop version (local profile vs. account-based) have not yet been designed; capabilities depend on that model. Cloud accounts, if any, belong to the future cloud synchronization phase.

### Future Scope

- Multi-device account support as part of cloud synchronization (see `Architecture.md` — Future Expansion).

### References

- `Architecture.md` — Module Architecture (Authentication module), Future Expansion
- `PROJECT.md` — Future Scope

## Session Management

### Purpose

Keeps the user's working context intact between uses: remaining signed in (once [Authentication](#authentication) is designed) and returning without losing state. Also relates to the browser sessions [Browser Automation](#browser-automation) maintains with job platforms, so the user does not have to log in to platforms for every run.

### Capabilities

#### TODO

Session Management has not yet been designed. The scope split between application sessions (user identity continuity) and automation browser sessions (platform logins) needs an architecture decision (see `docs/DECISIONS.md`).

### Future Scope

#### TODO

Session Management enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture
- `docs/DECISIONS.md`

## Search & Filtering

### Purpose

A cross-cutting capability: wherever EZApply presents lists of user data (applications, saved answers, resumes), the user can search and narrow them down as their data grows.

### Capabilities

#### TODO

Which views support search and filtering, and with what criteria, has not yet been designed. Job search across platforms (finding jobs to apply to) is a distinct capability whose design belongs to [Browser Automation](#browser-automation) and [Platform Management](#platform-management) and has not yet been specified.

### Future Scope

#### TODO

Search & Filtering enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture

## AI Resume Parsing

### Purpose

Extracts structured information from resumes uploaded through [Resume Management](#resume-management), so the user never types out what their resume already says. Extracted information populates the user's profile and [Saved Info](#saved-info) only after the user reviews and approves it — the system proposes, the user approves.

### Capabilities

- Extract structured information from an uploaded resume.
- Present extracted information to the user for review and correction.
- Feed approved information into the user's profile and saved information.

#### TODO

The set of fields extracted and the supported resume formats have not yet been designed.

### Future Scope

- Resume Optimization (see `PROJECT.md` — Future Scope).

### References

- `Architecture.md` — Module Architecture (Resume module), Architecture Constraints
- `PROJECT.md` — Solution (Resume Intelligence), Core Principles (User Control)

## Question Learning System

### Purpose

Builds the user's library of reusable answers as a byproduct of applying: when automation encounters a screening question with no saved answer, it pauses and asks the user; the answer is saved into [Saved Info](#saved-info) and reused automatically whenever the question appears again. Over time, the automation needs the user's input less and less.

### Capabilities

- Detect screening questions during automation runs that have no saved answer.
- Pause the run and ask the user for the answer.
- Save the user's answer for future reuse.
- Reuse saved answers when the same question appears again.

#### TODO

How question matching works from the user's perspective (exact repeats vs. recognizing rephrased questions) has not yet been designed.

### Future Scope

#### TODO

Question Learning System enhancements have not yet been designed.

### References

- `Architecture.md` — Module Architecture (Automation, Saved Information modules)
- `docs/Roadmap.md` — v0.9 (Analytics & Learning System)

## Platform Management

### Purpose

Defines which external job platforms EZApply can automate and lets the user manage per-platform preferences and access. Each supported platform is a target that [Browser Automation](#browser-automation) knows how to operate.

### Supported Platforms

- **LinkedIn** — TODO: support has not yet been designed.
- **Indeed** — TODO: support has not yet been designed.
- **Naukri** — TODO: support has not yet been designed.
- **Future Platforms** — adding a platform must be an extension, not a redesign (see `Architecture.md` — Architectural Principles: Extensibility). TODO: the criteria and process for adding new platforms have not yet been designed.

### Capabilities

- Enumerate the platforms EZApply supports.
- Let the user manage per-platform preferences and access.
- Provide platform targets to Browser Automation.

#### TODO

Per-platform capabilities and configuration have not yet been designed.

### Future Scope

- Support for additional platforms beyond LinkedIn, Indeed, and Naukri.
- A plugin system that could allow platform support to be extended (see `PROJECT.md` — Future Scope).

### References

- `Architecture.md` — Module Architecture, Architectural Principles (Extensibility)
- `PROJECT.md` — Future Scope

## Planned Features

All features above are **Planned** — specified at the product level in this document, with design gaps marked as TODO. Longer-horizon features (mobile applications, cloud synchronization, plugin system, and others) are owned by `PROJECT.md` — Future Scope.
