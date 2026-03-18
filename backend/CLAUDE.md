# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the development server
cd backend
uvicorn app.main:app --reload

# Install dependencies
pip install -r requirements.txt

# Database connectivity check
curl http://localhost:8000/db-check
```

No test infrastructure is configured yet.

## Tech Stack

- **Framework**: FastAPI with Uvicorn (ASGI)
- **Database**: PostgreSQL via SQLAlchemy 2.0 + psycopg2-binary
- **Vector Search**: pgvector (for embeddings/similarity search)
- **Validation**: Pydantic v2
- **Config**: python-dotenv loading from `backend/.env`

## Architecture

The app lives in `backend/app/` and follows a layered structure:

- **`config.py`** — loads and validates env vars (requires `DATABASE_URL`)
- **`db.py`** — SQLAlchemy engine + `SessionLocal` + `Base` declarative base; uses `pool_pre_ping=True`
- **`main.py`** — FastAPI app instance; mounts routers here
- **`models/`** — SQLAlchemy ORM models (one file per domain, extend `Base` from `db.py`)
- **`schemas.py`** — Pydantic request/response schemas
- **`routes/`** — FastAPI route handlers (one file per domain)
- **`services/`** — Business logic called by routes

New features follow the pattern: define model → define schema → implement service → wire up route → include router in `main.py`.

## Database

Uses **Google Cloud SQL** (PostgreSQL). Connection string is set via `DATABASE_URL` in `backend/.env`. pgvector is installed for vector similarity search — expect embedding columns on AI-related models.
