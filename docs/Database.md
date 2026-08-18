# EZApply — Database Architecture

This document describes the database schema, ORM configuration, and repositories.

For schema details and entity relationship models, refer to:
- [Architecture Guide](file:///d:/GitHub/EZapply/docs/Architecture.md)
- [Module Index](file:///d:/GitHub/EZapply/docs/MODULES.md)

## Technology Stack
- **Database**: SQLite (`backend/app.db`)
- **Driver**: `aiosqlite`
- **ORM**: SQLAlchemy 2.0 Async (`backend/app/database/connection.py`)

## Core Entities
1. **Application**: Tracks submitted job applications (`backend/app/models/application.py`)
2. **BotState**: Stores current bot configuration and runtime status (`backend/app/models/bot.py`)
3. **SavedInfo**: User profile, preferences, and custom questions (`backend/app/models/saved_info.py`)
4. **Resume**: Uploaded resumes metadata and parsed skill tags (`backend/app/models/resume.py`)
5. **QuestionAnswer**: Learned answers to custom application forms (`backend/app/models/question.py`)
