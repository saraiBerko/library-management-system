# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Backend**: Python + FastAPI, SQLAlchemy (ORM), Pydantic v2 (validation), Alembic (migrations), PostgreSQL. Python is the only backend language — do not introduce other runtimes for backend logic.
- **Frontend**: Vue 3 (Composition API, `<script setup>`) + Vite, Vue Router (screen navigation), Pinia (state + API calls), communicating with the backend exclusively via its REST API (no mocked data).
- **Infra**: Docker Compose runs `db` (Postgres), `backend`, and `frontend` as separate services.

## Commands

### Docker Compose (primary way to run the full stack)

```
docker compose up --build                              # start db + backend + frontend
docker compose exec backend python -m app.seed         # load sample data (10 books, 20 copies, 15 members, 31 loans)
docker compose exec backend alembic upgrade head        # only needed for a manual/out-of-band migration run
docker compose exec backend pytest                       # run backend tests inside the container
```

The backend container runs `alembic upgrade head` automatically on startup (see `backend/Dockerfile`), so the schema is ready as soon as `db` is healthy — no manual migration step for a normal `up`. Seeding is *not* automatic (`app/seed.py` clears the 5 tables before inserting), so it stays an explicit command.

Backend is served at `http://localhost:8000` (docs at `/docs`), frontend dev server at `http://localhost:5173`.

### Backend (from `backend/`)

```
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn app.main:app --reload                        # run API locally against a local Postgres

pytest                                                # run all tests
pytest tests/test_loans.py                            # run one test file
pytest tests/test_loans.py::test_create_and_return_loan_happy_path  # run a single test

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

### Domain model

`Author` and `Book` are many-to-many via a `book_authors` join table (defined as a plain `sa.Table` inside `app/models/book.py`, not its own entity — it has no independent schema/crud/router). `Copy` is a physical instance of a `Book` (`status`: `available` / `loaned` / `lost`, enforced by a CHECK constraint). `Member` and `Loan` round out the schema; a `Copy` is never linked directly to a `Member` — only through a `Loan` (`member_id` + `copy_id`). A partial unique index (`loans(copy_id) WHERE returned_date IS NULL`) guarantees at most one open loan per copy, which is also the concurrency guard for `POST /loans` (see the comment at the insert in `app/crud/loan.py`).

### Backend: layered, per-entity vertical slices

Each domain entity gets one file in each of four layers, named after the entity (e.g. `loan.py` in each):

- `app/models/` — SQLAlchemy `Mapped`/`mapped_column` declarative models (source of truth for DB schema).
- `app/schemas/` — Pydantic request/response models. Routers never accept or return SQLAlchemy models directly. `Author`/`Copy` only have read schemas (`AuthorRead`, `CopyRead`) since they're nested inside `Book`/`Loan` responses rather than exposed as their own resources.
- `app/crud/` — plain functions taking a `Session` and doing the actual DB reads/writes. Routers call into `crud`, not `db` directly. `app/core/exceptions.py` defines `NotFoundError`/`ConflictError`/`UnprocessableError`, raised from `crud/loan.py` where one function can fail in several distinct ways (see the mapping to 404/409/422 in `routers/loans.py`) — everywhere else a plain `if x is None: raise HTTPException(404, ...)` inline in the router is enough.
- `app/routers/` — `APIRouter`s that wire HTTP verbs/paths to `crud` functions. Registered on the `FastAPI` app in `app/main.py`. `GET /books` takes `q` (matches title OR author name), `genre`, `available`; `GET /loans` takes `open` to filter to un-returned loans.

`app/database.py` defines the SQLAlchemy `engine`, `SessionLocal`, declarative `Base`, and the `get_db` FastAPI dependency (yields a session, closes it after the request). `app/core/config.py` holds a `pydantic-settings` `Settings` object reading from environment variables / `.env` (`DATABASE_URL`, `CORS_ORIGINS`); import `settings` from there rather than reading `os.environ` directly.

`app/seed.py` populates sample data for local dev (see the Commands section); `backend/sql/queries.sql` holds four standalone analytical queries (books with no available copy, top-5 borrowers, books unborrowed in 12 months, avg loan duration by genre) written directly against the schema, independent of the ORM.

### Migrations

`alembic/env.py` imports `app.models` (all five models, via `app/models/__init__.py`) so autogenerate can diff against them — a new model must be imported there to be picked up. Migration `sqlalchemy.url` is taken from `Settings.database_url` at runtime, not hardcoded in `alembic.ini`.

### Frontend: Pinia stores own all API calls, views stay presentational

- `src/api/client.js` — a single configured `axios` instance (`baseURL` from `VITE_API_URL`) plus `extractErrorMessage()`, which normalizes FastAPI's error body (`detail` is a string for hand-raised errors, a list of `{msg, ...}` objects for automatic Pydantic validation errors) into one displayable string.
- `src/api/<entity>.js` — one file per entity exporting plain async functions that call the client and return `response.data`.
- `src/stores/` — Pinia stores (`books`, `members`, `loans`), one per entity area. **Stores are the only code that imports `api/*.js`.** Each store owns `loading`/`error` plus its data, and every action wraps its API call in try/catch, setting `error` via `extractErrorMessage()` on failure.
- `src/views/` — one component per screen (`BookSearchView`, `BookDetailView`, `LoanManagementView`), wired up in `src/router/index.js`. Views read store state and call store actions; they never call `api/*.js` directly.
- `src/components/` — small shared presentational pieces, e.g. `ErrorBanner.vue`.

### Docker Compose networking

Inside Compose, services reach each other by service name (`db`, `backend`), not `localhost` — e.g. the backend's `DATABASE_URL` host is `db`. The frontend's `VITE_API_URL` stays `http://localhost:8000` because it's resolved in the browser, not inside the container.
