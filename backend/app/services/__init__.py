"""
Service layer for business logic.

This package contains all application services that implement business logic.
Services are called by API routers and have access to the database and other layers.
"""
from app.services.automation_service import automation_service

__all__ = ["automation_service"]
