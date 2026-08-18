# EZApply — API Reference

This document outlines the REST API endpoints provided by the FastAPI backend.

For detailed architecture and endpoint flows, refer to:
- [Architecture Guide](file:///d:/GitHub/EZapply/docs/Architecture.md)
- [Module Index](file:///d:/GitHub/EZapply/docs/MODULES.md)
- [Workflow Specifications](file:///d:/GitHub/EZapply/docs/WORKFLOWS.md)

## Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

## Key Route Groups
1. `/api/v1/dashboard` — Overview statistics, funnels, and recent activity.
2. `/api/v1/bot` — Bot status, configuration, start/pause/stop lifecycle controls.
3. `/api/v1/saved-info` — User profile, saved keywords, answers, and templates.
4. `/api/v1/resumes` — Resume upload, text extraction, and default selection.
5. `/api/v1/analytics` — Application trends and platform conversion metrics.
