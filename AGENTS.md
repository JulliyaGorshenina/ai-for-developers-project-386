# AGENTS.md

Call-booking service ("cal.com lite"): FastAPI + SQLite backend, TypeScript +
Vite frontend. Two pages: guest booking (`/`) and owner admin (`/admin.html`).

## Repo map
- `backend/app/` — FastAPI app. Entrypoint `app.main:app`. `config.py` (env),
  `db.py` (schema + default schedule seed), `slots.py` (pure slot math),
  `repository.py`, `routers/` (availability, bookings, admin), `auth.py`.
- `backend/tests/` — pytest; `conftest.py` sets env and `sys.path`.
- `frontend/src/` — `main.ts` (booking page), `admin.ts` (owner page), `api.ts`,
  `types.ts`, `format.ts`.
- `.github/workflows/` — `ci.yml`, `release-please.yml`, `hexlet-check.yml`.

## Do not touch
- `.github/workflows/hexlet-check.yml` and the repository name — Hexlet grading
  depends on them (do not delete, edit, or rename).
- `[tool.ruff.lint] ignore = ["B008"]` in `backend/pyproject.toml`: FastAPI
  `Depends(...)` defaults are intentional; do not "fix" B008.

## Dependencies (non-obvious)
- Backend runtime + dev deps live in `backend/requirements.txt` — this is what
  setup and CI install. Add new deps there too (pyproject `dependencies`/`[dev]`
  are informational; CI does not install the extra).
- `tzdata` is required: `zoneinfo` has no OS timezone database on Windows.
- Frontend deps in `frontend/package.json`; CI runs `npm ci`, so keep
  `frontend/package-lock.json` in sync.

## Commands (from repo root)
Backend:
```
& "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" -m venv backend\.venv   # one-time (venv already exists)
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend  # http://127.0.0.1:8000, /docs
backend\.venv\Scripts\python -m pytest backend                 # all backend tests
backend\.venv\Scripts\python -m pytest backend -k test_slots   # single test
backend\.venv\Scripts\python -m ruff check backend
backend\.venv\Scripts\python -m ruff format --check backend
```
`python` is not on PATH on this machine — use `backend\.venv\Scripts\python` (or
the full path above).

Frontend:
```
cd frontend
npm install
npm run dev        # :5173, proxies /api -> :8000
npm run lint       # eslint
npm run typecheck  # tsc --noEmit
npm test           # vitest
npm run build      # tsc --noEmit && vite build -> frontend/dist
```

## Testing notes
- `conftest.py` sets `DB_PATH` (temp dir) and `ADMIN_TOKEN=test-token` at import
  time, before `app` is imported. Import `app` inside test modules, as the
  existing tests do.
- Use `with TestClient(app) as client:` — the lifespan seeds the default weekly
  schedule; without the context manager the DB has no tables.
- SPA static files are mounted only if `frontend/dist` exists when `app.main` is
  imported. API tests do not cover this; build the frontend to test `/`.

## Conventions / gotchas
- Admin endpoints require header `X-Admin-Token` == `ADMIN_TOKEN`.
- Time: slots are generated in `BOOKING_TZ`, stored/returned as UTC ISO; the
  frontend renders in the browser timezone.
- Frontend is multi-page: adding an HTML entry requires updating
  `build.rollupOptions.input` in `frontend/vite.config.ts`.
- Versioning is owned by release-please: bump via Conventional Commits;
  `version.txt` and `CHANGELOG.md` are managed. `backend/pyproject.toml` version
  is NOT auto-synced (`release-type: simple`) — update it manually if needed.

## Env vars (backend)
| Variable             | Default               | Purpose                          |
| -------------------- | --------------------- | -------------------------------- |
| `ADMIN_TOKEN`        | `dev-admin-token`     | Token for the owner/admin API    |
| `BOOKING_TZ`         | `Europe/Moscow`       | Timezone used to render slots    |
| `SLOT_MINUTES`       | `30`                  | Slot length in minutes           |
| `AVAILABILITY_DAYS`  | `14`                  | Days returned by `/availability` |
| `DB_PATH`            | `backend/bookings.db` | SQLite database file             |

## CI
`ci.yml` runs on every push and PR — backend: `ruff check` -> `ruff format
--check` -> `pytest`; frontend: `npm ci` -> lint -> typecheck -> test -> build.
Keep it green (Python 3.12, Node 22).

## Commit message convention — REQUIRED
All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<optional scope>): <description>` (`feat`, `fix`, `chore`, `docs`,
`refactor`, `test`, `ci`, `build`, `perf`, `style`; optional scope `backend`,
`frontend`, `ci`). Breaking changes: `!` after type/scope or a `BREAKING CHANGE:`
footer. This is mandatory because `release-please`
(`.github/workflows/release-please.yml`) reads the history to build the changelog
and bump the version (SemVer). Note: release-please also needs the repository
setting "Allow GitHub Actions to create and approve pull requests"
(Settings > Actions > General), otherwise the workflow fails.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`GLOSSARY.md` and `docs/adr/` at the repo root). See `docs/agents/domain.md`.
