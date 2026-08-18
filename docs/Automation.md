# EZApply — Automation Architecture

This document describes the browser automation engine and platform integrations.

For technical deep dives, refer to:
- [Architecture Guide](file:///d:/GitHub/EZapply/docs/Architecture.md)
- [Module Index](file:///d:/GitHub/EZapply/docs/MODULES.md)
- [Feature Catalog](file:///d:/GitHub/EZapply/docs/FEATURES.md)

## Automation Engine Overview
- **Engine**: Playwright Python (`backend/app/automation/engine.py`)
- **Platforms**:
  - LinkedIn (`backend/app/automation/platforms/linkedin.py`)
  - Indeed (`backend/app/automation/platforms/indeed.py`)
- **Session Management**: `backend/app/automation/session_manager.py`
- **Form Filler**: `backend/app/automation/form_filler.py`
