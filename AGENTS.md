# AGENTS.md

Call-booking service ("cal.com lite"): FastAPI + SQLite backend, TypeScript +
Vite frontend. Three pages: landing (`/`), guest booking (`/booking.html`) and
owner admin (`/admin.html`). The API is contract-first: TypeSpec is the source of
truth (see `spec/`).

## Repo map
- `spec/` — TypeSpec contract (`main.tsp`, `tspconfig.yaml`, `package.json`).
  Emits OpenAPI 3.1 JSON to `spec/openapi/openapi.json` (committed).
- `backend/app/` — FastAPI app. Entrypoint `app.main:app`. `config.py` (env),
  `db.py` (schema + seeds), `slots.py` (pure slot math), `repository.py`
  (queries + conflict logic), `routers/` (event_types, availability, bookings,
  schedule).
- `backend/app/generated/models.py` — generated Pydantic v2 models (do not edit).
- `frontend/src/` — `main.ts` (booking page), `admin.ts` (owner page),
  `api.ts` (thin wrapper over the generated SDK), `format.ts`.
- `frontend/src/api/generated/` — generated TS SDK (do not edit).
- `e2e/` — Playwright end-to-end tests (repo root).
- `.github/workflows/` — `ci.yml`, `release-please.yml`, `hexlet-check.yml`.

## Do not touch
- `.github/workflows/hexlet-check.yml` and the repository name — Hexlet grading
  depends on them (do not delete, edit, or rename).
- `[tool.ruff.lint] ignore = ["B008"]` in `backend/pyproject.toml`: FastAPI
  `Depends(...)` defaults are intentional; do not "fix" B008.
- Everything under `spec/openapi/`, `backend/app/generated/` and
  `frontend/src/api/generated/` is machine-written — regenerate it, never edit.

## Contract pipeline (change order)
Edit the TypeSpec, regenerate, then change both sides. Never hand-write an API
call next to the generated SDK.

```powershell
# backend\ and frontend\ generation need Node on PATH (see below)
cd spec; npm install; npx tsp compile .          # -> spec/openapi/openapi.json
cd ..\frontend; npm install; npm run gen:api      # -> src/api/generated/
cd ..; backend\.venv\Scripts\python -m datamodel_code_generator `
  --input spec\openapi\openapi.json --input-file-type openapi `
  --output-model-type pydantic_v2.BaseModel --openapi-scopes schemas `
  --target-python-version 3.12 --disable-timestamp `
  --output backend\app\generated\models.py
```

CI (`contract` job) regenerates all three and runs `git diff --exit-code`, so a
spec change that isn't regenerated fails the build.

## Dependencies (non-obvious)
- Backend runtime + dev deps live in `backend/requirements.txt` (what setup and CI
  install). It includes `datamodel-code-generator` (pinned) for model generation.
- `tzdata` is required: `zoneinfo` has no OS timezone database on Windows.
- Frontend deps in `frontend/package.json` (includes `@hey-api/openapi-ts` and
  `@hey-api/client-fetch`, pinned exact); CI runs `npm ci`, so keep
  `frontend/package-lock.json` in sync.
- Root `package.json` holds the Playwright e2e tooling.

## Commands (from repo root)
Backend:
```
backend\.venv\Scripts\python -m pip install -r backend\requirements.txt
backend\.venv\Scripts\python -m uvicorn app.main:app --reload --app-dir backend  # http://127.0.0.1:8000, /docs
backend\.venv\Scripts\python -m pytest backend
backend\.venv\Scripts\python -m ruff check backend
backend\.venv\Scripts\python -m ruff format --check backend
```
`python` is not on PATH on this machine — use `backend\.venv\Scripts\python`.

Frontend:
```
cd frontend
npm install
npm run dev        # :5173, proxies /api -> :8000
npm run lint       # eslint
npm run typecheck  # tsc --noEmit
npm test           # vitest
npm run build      # tsc --noEmit && vite build -> frontend/dist
npm run gen:api    # regenerate the SDK from spec/openapi/openapi.json
```

E2E (Playwright; needs `frontend/dist` built, Chromium installed):
```
cd frontend; npm run build; cd ..
npm install
npx playwright install chromium
npx playwright test
```

### Node.js / TypeSpec toolchain

`node`/`npm` are not on PATH. A portable LTS build is at
`%LOCALAPPDATA%\nodejs\node-v24.22.1-win-x64`; prepend it before frontend,
TypeSpec or e2e commands:

```powershell
$env:PATH = "$env:LOCALAPPDATA\nodejs\node-v24.22.1-win-x64;" + $env:PATH
```

## Testing notes
- `conftest.py` gives every test its own seeded SQLite DB (`fresh_db` fixture) and
  a `client` fixture (`TestClient` with lifespan).
- Use the `client` fixture (or `with TestClient(app) as client:`) — the lifespan
  seeds event types and the default weekly schedule.
- `backend/tests/test_contract.py` guards that the app exposes exactly the
  committed contract's paths.
- SPA static files are mounted only if `frontend/dist` exists when `app.main` is
  imported; build the frontend before e2e.

## Conventions / gotchas
- Server-side rules: a slot is offerable only if it is on the type's grid, inside
  the schedule, in the future and conflict-free. Conflicts are interval overlaps
  across **all** event types (see ADR 0003); back-to-back is allowed.
- Owner endpoints are unauthenticated (single predefined owner); there is no
  `X-Admin-Token`.
- Time: slots are generated in `BOOKING_TZ`, stored/returned as UTC ISO; the
  frontend renders in the browser timezone.
- SQLite connections use `check_same_thread=False` (FastAPI may run the dependency
  and endpoint on different threadpool threads).
- Frontend is multi-page: adding an HTML entry requires updating
  `build.rollupOptions.input` in `frontend/vite.config.ts`.
- Versioning is owned by release-please (`release-type: simple`); `version.txt` and
  `CHANGELOG.md` are managed. `backend/pyproject.toml` version is NOT auto-synced.

## Env vars (backend)
| Variable            | Default               | Purpose                          |
| ------------------- | --------------------- | -------------------------------- |
| `BOOKING_TZ`        | `Europe/Moscow`       | Timezone used to render slots    |
| `AVAILABILITY_DAYS` | `14`                  | Days returned by `/availability` |
| `DB_PATH`           | `backend/bookings.db` | SQLite database file             |

## CI
`ci.yml` runs on every push and PR:
- `contract` — TypeSpec → OpenAPI → SDK/models, then `git diff --exit-code`.
- `backend` — `ruff check` → `ruff format --check` → `pytest`.
- `frontend` — `npm ci` → lint → typecheck → test → build.
- `e2e` — Playwright happy path (blocking; report uploaded on failure).
Keep it green (Python 3.12, Node 22).

## Commit message convention — REQUIRED
All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/):
`<type>(<optional scope>): <description>` (`feat`, `fix`, `chore`, `docs`,
`refactor`, `test`, `ci`, `build`, `perf`, `style`; optional scope `backend`,
`frontend`, `spec`, `ci`). Breaking changes: `!` after type/scope or a
`BREAKING CHANGE:` footer. Mandatory because `release-please` reads the history to
build the changelog and bump the version (SemVer). Note: release-please also needs
the repository setting "Allow GitHub Actions to create and approve pull requests".

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout (`GLOSSARY.md` and `docs/adr/` at the repo root). See `docs/agents/domain.md`.
