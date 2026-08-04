# Library Management System

A library management system: books with multiple authors, physical copies, members, and loans. Built as a FastAPI + PostgreSQL backend with a Vue 3 frontend.

## Prerequisites

- **Docker** with the Compose plugin (Docker Desktop on Mac/Windows, or Docker Engine + `docker-compose-plugin` on Linux). This is the only hard requirement — the instructions below assume it's the only thing installed.

Running the backend or frontend outside Docker is also possible, but needs Python 3.12, Node 20, and a local PostgreSQL instance — not required for the steps below.

## Getting started

```
git clone https://github.com/saraiBerko/library-management-system.git && cd library-management-system
```

From the repository root:

```
docker compose up --build
```

This builds and starts three services: `db` (Postgres 16), `backend` (FastAPI on `http://localhost:8000`), and `frontend` (Vue dev server on `http://localhost:5173`). The backend automatically waits for Postgres to be healthy and runs `alembic upgrade head` before starting — the database schema is ready by the time the container is up, no manual migration step needed.

Once all three services are running, load some data:

```
docker compose exec backend python -m app.seed
```

Then open:

- Frontend: http://localhost:5173
- API: http://localhost:8000 (interactive docs at http://localhost:8000/docs)

## Configuration

Configuration is environment-variable based. `.env.example` lists the configurable variables: `DATABASE_URL` (backend, Postgres connection string), `CORS_ORIGINS` (backend, allowed frontend origins), and `VITE_API_URL` (frontend, where the browser sends API requests). `docker-compose.yml` already sets sensible defaults for all three, so no `.env` file is needed to run `docker compose up --build`.

The backend's port is also configurable independently via `PORT`, honored by the Dockerfile's `CMD` (e.g. `docker run -e PORT=9000 ...`) — separate from Compose's own host-port mapping.

## Troubleshooting

**`permission denied while trying to connect to the Docker daemon socket` (WSL/Linux)**: your user isn't in the `docker` group yet. Fix it with:

```
sudo usermod -aG docker $USER
```

Then close and reopen your WSL/terminal session (or run `newgrp docker`) so the group membership takes effect, and retry `docker compose up --build`.

## Seed data

`docker compose exec backend python -m app.seed` inserts 10 books (13 authors, some books with multiple authors), 20 copies in a mix of `available`/`loaned`/`lost` statuses, 15 members (a few inactive), and 31 loans spanning roughly the last two years — a mix of returned, open, and overdue, so every screen and report has something to show. It's safe to re-run: it clears the 5 tables first, so running it again just resets to the same deterministic dataset.

## Running tests

```
docker compose exec backend pytest
```

## Architecture

**Backend** (`backend/app/`) is a layered, per-entity FastAPI app: `models/` (SQLAlchemy), `schemas/` (Pydantic request/response), `crud/` (DB logic), `routers/` (HTTP layer) — routers call into `crud`, never the DB session directly. Migrations are managed with Alembic (`backend/alembic/`).

Beyond the assignment's 6 required endpoints, two small additional ones exist: `GET /members` (lists all members, needed for the member picker on the loan-management screen) and `GET /loans?open=true` (lists every open loan across all members, needed for that screen's open-loans table — `GET /reports/overdue` only covers the subset that's already overdue).

**Frontend** (`frontend/src/`) is Vue 3 with Vue Router (3 screens under `views/`) and Pinia (`stores/`) — components never call the API directly; each store owns its slice of state and the `api/*.js` calls that populate it, giving one consistent loading/error-handling path across the app.

**Database**: PostgreSQL. `Book`s and `Author`s are many-to-many via a `book_authors` join table; a `Copy` is a physical instance of a `Book` and is only ever linked to a `Member` indirectly, through a `Loan` — there's no direct copy-to-member reference anywhere in the schema.

Inside Docker Compose, services reach each other by service name (the backend's `DATABASE_URL` host is `db`), but the frontend's `VITE_API_URL` stays `http://localhost:8000` because it's resolved in the browser, not inside the container.

## Project layout

- `backend/sql/queries.sql` — four standalone analytical SQL queries (books with no available copies, top 5 borrowers in the last year, books unborrowed in 12 months, average loan duration by genre), independent of the ORM.
- `backend/alembic/versions/` — the schema migration.
- `backend/app/seed.py` — the seed script described above.
