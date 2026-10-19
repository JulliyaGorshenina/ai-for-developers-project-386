# AGENTS.md

Guidance for AI agents (and humans) working in this repository.

## Project overview

A small call-booking service ("cal.com lite"):

- **backend/** — Python + FastAPI + SQLite. Publishes free 30-minute slots from
  a weekly schedule, accepts bookings, and lets the calendar owner view and
  cancel upcoming meetings. No accounts, no auth beyond a simple admin token.
- **frontend/** — TypeScript + Vite (vanilla TS). A booking page for guests and
  an admin page for the owner.

## Layout

```
backend/app/       FastAPI application (config, db, slots, auth, routers)
backend/tests/     pytest suite
frontend/src/      TypeScript sources (main.ts, admin.ts, api.ts, types.ts)
frontend/          Vite project (index.html, admin.html, configs)
.github/workflows/ CI + release-please + hexlet-check (do not touch the latter)
```

## Prerequisites

- Python 3.10+ (developed on 3.14)
- Node.js LTS (for the frontend build)

> On this Windows machine `python` is not on `PATH`; use
> `& "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe"` instead.

## Backend

```powershell
# one-time setup
& "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt

# run (http://127.0.0.1:8000, docs at /docs)
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend

# tests
backend\.venv\Scripts\python -m pytest backend

# lint
backend\.venv\Scripts\python -m ruff check backend
backend\.venv\Scripts\python -m ruff format --check backend
```

## Frontend

```powershell
cd frontend
npm install

npm run dev        # Vite dev server on :5173, proxies /api -> :8000
npm run build      # type-check + production build into frontend/dist
npm run lint       # eslint
npm run typecheck  # tsc --noEmit
npm test           # vitest
```

The production build in `frontend/dist` is served by the backend at `/`.

## Environment variables (backend)

| Variable       | Default              | Purpose                          |
| -------------- | -------------------- | -------------------------------- |
| `ADMIN_TOKEN`  | `dev-admin-token`    | Token for the owner/admin API    |
| `BOOKING_TZ`   | `Europe/Moscow`      | Timezone used to render slots    |
| `SLOT_MINUTES` | `30`                 | Slot length in minutes           |
| `DB_PATH`      | `backend/bookings.db`| SQLite database file             |

## CI

`.github/workflows/ci.yml` runs on every push and pull request: it lints and
tests the backend (ruff + pytest) and lints, type-checks, tests and builds the
frontend. Keep it green.

## Commit message convention — REQUIRED

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <description>
```

Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`, `build`,
`perf`, `style`. Use an optional scope such as `backend`, `frontend` or `ci`.

Examples:

```
feat(backend): add weekly availability schedule endpoint
fix(frontend): handle empty slot list
ci: add release-please workflow
```

This is mandatory because `release-please` (see
`.github/workflows/release-please.yml`) reads the commit history to build the
changelog and bump the version following Semantic Versioning. Breaking changes
are marked with `!` after the type/scope (e.g. `feat(api)!: ...`) or a
`BREAKING CHANGE:` footer. Agents author most commits here, so this rule applies
to them directly.
