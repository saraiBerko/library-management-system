# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Backend**: Python + FastAPI, SQLAlchemy (ORM), Pydantic v2 (validation), Alembic (migrations), PostgreSQL. Python is the only backend language — do not introduce other runtimes for backend logic.
- **Frontend**: Vue 3 (Composition API, `<script setup>`) + Vite, communicating with the backend exclusively via its REST API (no mocked data).
- **Infra**: Docker Compose runs `db` (Postgres), `backend`, and `frontend` as separate services.

## Commands

### Docker Compose (primary way to run the full stack)

```
docker compose up --build          # start db + backend + frontend
docker compose exec backend alembic upgrade head   # apply migrations inside the container
```

Backend is served at `http://localhost:8000`, frontend dev server at `http://localhost:5173`.

### Backend (from `backend/`)

```
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn app.main:app --reload                        # run API locally against a local Postgres

pytest                                                # run all tests
pytest tests/test_books.py                            # run one test file
pytest tests/test_books.py::test_create_and_list_books  # run a single test

alembic revision --autogenerate -m "message"          # generate a migration from model changes
alembic upgrade head                                  # apply migrations
alembic downgrade -1                                  # roll back one migration
```

Tests use an in-memory SQLite database (see `tests/conftest.py`), not Postgres, so they run without any external services.

### Frontend (from `frontend/`)

```
npm install
npm run dev        # Vite dev server on :5173
npm run build       # production build
npm run preview     # preview the production build
```

## Architecture

### Backend: layered, per-entity vertical slices

Each domain entity gets one file in each of four layers, all named after the entity (e.g. `book.py` in each):

- `app/models/` — SQLAlchemy `Mapped`/`mapped_column` declarative models (source of truth for DB schema).
- `app/schemas/` — Pydantic request/response models (`XCreate`, `XUpdate`, `XRead`). Routers never accept or return SQLAlchemy models directly.
- `app/crud/` — plain functions taking a `Session` and doing the actual DB reads/writes. Routers call into `crud`, not `db` directly, so DB logic stays out of the HTTP layer.
- `app/routers/` — `APIRouter`s that wire HTTP verbs/paths to `crud` functions and handle 404s. Registered on the `FastAPI` app in `app/main.py`.

`app/database.py` defines the SQLAlchemy `engine`, `SessionLocal`, declarative `Base`, and the `get_db` FastAPI dependency (yields a session, closes it after the request). `app/core/config.py` holds a `pydantic-settings` `Settings` object reading from environment variables / `.env` (`DATABASE_URL`, `CORS_ORIGINS`); import `settings` from there rather than reading `os.environ` directly.

When adding a new entity, follow the `Book` slice (`app/models/book.py`, `app/schemas/book.py`, `app/crud/book.py`, `app/routers/books.py`) as the template, then register the new router in `app/main.py`.

### Migrations

`alembic/env.py` imports `Base` and all models from `app.models` so autogenerate can diff against them — new models must be imported in `app/models/__init__.py` to be picked up. Migration `sqlalchemy.url` is taken from `Settings.database_url` at runtime, not hardcoded in `alembic.ini`.

### Frontend: thin API-client + components

- `src/api/client.js` — a single configured `axios` instance (`baseURL` from `VITE_API_URL`); all HTTP calls go through it.
- `src/api/<entity>.js` — one file per entity exporting plain async functions (`getBooks`, `createBook`, ...) that call the client and return `response.data`. Components import these rather than calling `axios` directly.
- `src/components/` — feature components (e.g. `BookList.vue`) own their own data fetching via the `onMounted` + `ref` pattern and call the `api/` functions.

### Docker Compose networking

Inside Compose, services reach each other by service name (`db`, `backend`), not `localhost` — e.g. the backend's `DATABASE_URL` host is `db`. The frontend's `VITE_API_URL` stays `http://localhost:8000` because it's resolved in the browser, not inside the container.
