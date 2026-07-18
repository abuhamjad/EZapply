# EZApply Backend

FastAPI backend for EZApply job application automation platform.

## Structure

- `app/` - Main application package
  - `api/` - API routes
  - `core/` - Core configuration and utilities
  - `database/` - Database configuration
  - `models/` - Database models
  - `schemas/` - Pydantic schemas
  - `repositories/` - Data access layer
  - `services/` - Business logic layer
  - `automation/` - Automation logic
  - `dependencies/` - Dependency injection
  - `utils/` - Utility functions
  - `main.py` - FastAPI application entry point
- `tests/` - Test suite
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Fill in your API keys and database credentials in `.env`:
   ```env
   DATABASE_URL="postgresql://user:password@host:port/database"
   OPENAI_API_KEY="your-openai-api-key"
   NAUKRI_EMAIL="your-email"
   NAUKRI_PASSWORD="your-password"
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Access the API at `http://localhost:8000`

## API Documentation

See the interactive API documentation at `http://localhost:8000/docs`.
