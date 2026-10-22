# Research: TypeSpec and the contract-generation chain for booking-service

Ticket: **R1 — "Research: TypeSpec и цепочка генерации контракта"**

Goal: define how a single TypeSpec source can drive (a) an OpenAPI 3 document,
(b) a TypeScript client for the vanilla-TS + Vite frontend, and (c) Pydantic /
FastAPI artifacts for the backend, and how to wire that into this repo's CI.

All claims are cited to primary sources (official docs, first-party repos).
Research date: **October 2026**.

---

## 1. What TypeSpec is, and how entities/endpoints are described

TypeSpec is Microsoft's language for describing APIs. A `.tsp` program is compiled
by the `tsp` CLI; *emitters* translate the compiled program into other formats
(OpenAPI, JSON Schema, protobuf, clients, …).

### Entities (models)

Data shapes are `model` declarations — records of named, typed properties
([Models — TypeSpec docs](https://typespec.io/docs/language-basics/models/)):

```typespec
model Booking {
  id: int32;
  slot_start: string;
  slot_end: string;
  name: string;
  email: string;
  comment: string;
  status: string;
  created_at: string;
}
```

- Optional properties use `?` (`address?: string`).
- Defaults use `=` (`age: uint8 = 0`).
- Composition: `...Spread` copies members; `is` creates an exact copy including
  decorators; `extends` creates a nominal inheritance relationship.
- Constraints come from decorators (`@minLength`, `@maxValue`, …).
- Enums model closed value sets.

This maps directly onto the project's `backend/app/schemas.py` models
(`Slot`, `DaySlots`, `BookingCreate`, `Booking`, `Window`, `ScheduleUpdate`) and
`frontend/src/types.ts`.

### Endpoints (operations)

Operations are `op` declarations; HTTP verbs and paths come from the
`@typespec/http` library ([OpenAPI v3 emitter guide](https://typespec.io/docs/emitters/openapi3/openapi/)):

```typespec
@route("/api")
namespace BookingService;

@route("/availability")
@get
op getAvailability(@query days?: int32): DaySlots[];

@route("/bookings")
@post
op createBooking(@body body: BookingCreate): Booking;

@route("/admin/bookings/{id}")
@delete
op cancelBooking(@path id: int32, @header "X-Admin-Token" token: string): Booking;
```

- Verbs: `@get`, `@post`, `@put`, `@patch`, `@delete` (inferred from the name if omitted).
- Parameter location: `@path`, `@query`, `@header`; everything else is the request
  body (or use `@body` explicitly).
- `@route` can be applied to operations, interfaces, and namespaces; nested routes
  are concatenated (`@route("/api")` + `@route("/bookings")` → `/api/bookings`).
- The service is declared with `@service(#{ title: "…" })` and `@server(url, desc)`.

### Versioning

Add `@typespec/versioning` and annotate the service
([Versioning guide](https://typespec.io/docs/getting-started/getting-started-rest/06-versioning/)):

```typespec
import "@typespec/versioning";
using Versioning;

@versioned(Versions)
namespace BookingService;

enum Versions { v1: "1.0" }
```

`@added` / `@removed` mark version-scoped members. The OpenAPI emitter then writes
one document **per version** (`openapi.v1.yaml`, `openapi.v2.yaml`, …). This project
is at a single implicit version, so versioning can be adopted later without
restructuring the spec.

### The OpenAPI emitter

The emitter is **`@typespec/openapi3`** — "TypeSpec library for emitting OpenAPI
3.0 and OpenAPI 3.1 from the TypeSpec REST protocol binding"
([package README](https://github.com/microsoft/typespec/blob/main/packages/openapi3/README.md),
[emitter reference](https://typespec.io/docs/emitters/openapi3/reference/emitter/)).

- Run: `tsp compile . --emit=@typespec/openapi3`, or list it under `emit:` in
  `tspconfig.yaml`.
- Options: `file-type` (`yaml` | `json` | both), `output-file`, `openapi-versions`
  (`3.0.0` default, `3.1.0`, `3.2.0`), `emitter-output-dir`, `new-line`.
- Default output path: `{output-dir}/@typespec/openapi3/…`.

For this project, emit **OpenAPI 3.1 as JSON** (best-supported by the downstream
generators below): `openapi-versions: ["3.1.0"]`, `file-type: json`.

---

## 2. TypeScript SDK generation from OpenAPI — recommendation

Candidates compared: `openapi-typescript` + `openapi-fetch`, `orval`,
`openapi-generator` (`typescript-fetch`), `@hey-api/openapi-ts`.

### ⚠️ Critical, current finding: `openapi-typescript` / `openapi-fetch` are in maintenance mode

The maintainer announced the 2026 roadmap putting `openapi-fetch`,
`openapi-react-query`, and `openapi-metadata` into maintenance mode
([discussion #2559](https://github.com/openapi-ts/openapi-typescript/discussions/2559)),
and then in **September 2026** announced that **`openapi-typescript` itself is
also in maintenance mode and will receive no further updates**
([issue #2874](https://github.com/openapi-ts/openapi-typescript/issues/2874)).
The docs even recommend migrating to another project. **Do not start a new
codebase on `openapi-typescript` + `openapi-fetch` in 2026.**

### Comparison

| Tool | Runtime footprint | OpenAPI 3.1 | Framework fit | Maintenance (Oct 2026) |
| --- | --- | --- | --- | --- |
| `openapi-typescript` + `openapi-fetch` | types-only + ~3–6 kB client | yes | framework-agnostic | **maintenance mode / no updates** |
| `orval` | generated fetch/axios client (+ React Query/SWR hooks) | yes (also Swagger 2.0) | React/Vue/Svelte/Angular hooks; TS-first | active |
| `openapi-generator` (`typescript-fetch`) | full SDK, verbose | partial/varies | polyglot, 50+ languages | active but heavy (Java runtime) |
| **`@hey-api/openapi-ts`** | generated SDK + pluggable fetch client | yes | framework-agnostic, Vite plugin, 20+ plugins | active, strong adoption |

Sources: [OpenAPI TS generator comparison](https://www.speakeasy.com/docs/sdks/languages/typescript/oss-comparison-ts),
[nestjs-openapi recipes](https://nestjs-openapi.vercel.app/docs/recipes/openapi-clients),
[hey-api get-started](https://heyapi.dev/docs/openapi/typescript/get-started).

### Recommendation: `@hey-api/openapi-ts` + `@hey-api/client-fetch`

- **Framework-agnostic.** This frontend is vanilla TS + Vite with no React, so
  orval's headline feature (TanStack Query hooks) is dead weight. hey-api produces
  plain typed SDK functions callable from `api.ts`.
- **First-class Vite integration.** There is an official `@hey-api/vite-plugin`
  for Vite 5/6/7/8 (this repo is on Vite 6), so generation can hook into the build.
- **Active and widely adopted** (Vercel, OpenCode, PayPal per the docs).
- **OpenAPI 3.1 supported.**

Generated layout (e.g. `frontend/src/api/generated/`): `client.ts`, `types.gen.ts`,
`services.gen.ts` — importable directly by the existing `frontend/src/api.ts`,
which can drop its hand-written `fetch` wrapper and the duplicated
`frontend/src/types.ts`.

> Pin an exact version: hey-api publishes `@hey-api/openapi-ts` under 0.x
> ("initial development"), so use `-E` / exact versions and read migration notes.

---

## 3. Backend generation from OpenAPI — recommendation

Candidates: `datamodel-code-generator`, `openapi-python-client`,
`fastapi-code-generator`.

- **`datamodel-code-generator`** turns OpenAPI 3 / JSON Schema / others into
  Pydantic v2 models, dataclasses, TypedDict, or msgspec
  ([repo](https://github.com/koxudaxi/datamodel-code-generator/)). It also gained
  **experimental** FastAPI server generation (`--generate-server fastapi`) that
  writes a `app/server/` package (routers + a service `Protocol` per operation
  group) alongside the models
  ([target-generation options](https://datamodel-code-generator.koxudaxi.dev/cli-reference/target-generation-options/)).
- **`openapi-python-client`** generates an `attrs`-based *HTTP client*, not
  FastAPI routes; using Pydantic with it requires template surgery
  ([repo](https://github.com/openapi-generators/openapi-python-client/),
  [discussion #1049](https://github.com/openapi-generators/openapi-python-client/discussions/1049)).
  Wrong shape for a server.
- **`fastapi-code-generator`** is a thin wrapper that "uses
  datamodel-code-generator to build the model layer"
  ([repo](https://github.com/koxudaxi/fastapi-code-generator)); it is a strict
  subset of what `datamodel-code-generator` now does natively, and upstream
  documents a migration path to `datamodel-codegen --generate-server fastapi`
  ([migration guide](https://datamodel-code-generator.koxudaxi.dev/fastapi-code-generator-migration/)).

### Recommendation: `datamodel-code-generator`, models-first

Use it to generate **Pydantic v2 models** from the emitted OpenAPI JSON:

```bash
datamodel-codegen \
  --input spec/openapi/openapi.json \
  --input-file-type openapi \
  --output-model-type pydantic_v2.BaseModel \
  --openapi-scopes schemas api \
  --target-python-version 3.12 \
  --output backend/app/generated/models.py
```

Why: it is the most-used Pydantic generator, actively maintained, supports
OpenAPI 3.1 and Pydantic v2, and is the same engine `fastapi-code-generator` is
built on. The project's `backend/app/schemas.py` is already Pydantic v2, so the
generated models drop in with no adapter.

**Caveat — do not auto-generate the routers yet.** FastAPI server generation is
explicitly **experimental** ("its options, generated package, template values, and
served OpenAPI document may change"). This backend has hand-written business logic
in `routers/`, `repository.py`, and `slots.py`; generated route stubs would fight
that. Generate models (the contract) and keep routers hand-written. Revisit
`--generate-server fastapi` only when it stabilises.

---

## 4. Repo layout, npm scripts, and CI wiring

### Recommended layout

```
spec/                              # TypeSpec source of truth (hand-written)
  main.tsp
  tspconfig.yaml
  package.json                     # pins @typespec/compiler, http, openapi3, versioning
  package-lock.json
  openapi/                         # COMMITTED generated OpenAPI 3.1 (JSON)
    openapi.json
frontend/src/api/generated/        # COMMITTED generated TS client (hey-api)
  client.ts  types.gen.ts  services.gen.ts
backend/app/generated/             # COMMITTED generated Pydantic models
  models.py
```

**Commit the generated artifacts.** Rationale specific to this repo: Node/npm are
**not installed on the local machine**, so generated TS cannot be rebuilt locally;
CI runs `npm ci` and the build must be self-contained. Committing also makes
contract changes reviewable in the PR diff. Guard against drift with a CI job that
regenerates and fails on a non-empty `git diff` (see below).

### npm scripts

In `spec/package.json` (TypeSpec side):

```json
{
  "scripts": {
    "build": "tsp compile .",
    "watch": "tsp compile . --watch"
  },
  "devDependencies": {
    "@typespec/compiler": "<pinned>",
    "@typespec/http": "<pinned>",
    "@typespec/openapi3": "<pinned>",
    "@typespec/versioning": "<pinned>"
  }
}
```

In `frontend/package.json` (client side) — add generation next to the existing
scripts (`dev`, `build`, `lint`, `typecheck`, `test`):

```json
{
  "scripts": {
    "gen:api": "openapi-ts -i ../spec/openapi/openapi.json -o src/api/generated"
  },
  "devDependencies": {
    "@hey-api/openapi-ts": "<exact version>",
    "@hey-api/client-fetch": "<exact version>"
  }
}
```

Backend generation is a Python step; document it in `AGENTS.md` (e.g.
`backend\Scripts\python -m datamodel_code_generator …`) and pin
`datamodel-code-generator` in `backend/requirements.txt` (this is what setup and
CI install — see `AGENTS.md`).

### CI wiring (extend `.github/workflows/ci.yml`)

The current CI has a `backend` job (ruff + pytest) and a `frontend` job
(`npm ci` → lint → typecheck → test → build). Add a **contract** job that runs
first, or a drift-check step, using Node 22 (already the CI Node version) and
Python 3.12:

```yaml
  contract:
    name: Contract (TypeSpec → OpenAPI → SDK/models)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Emit OpenAPI
        working-directory: spec
        run: npm ci && npx tsp compile .
      - name: Generate TS client
        working-directory: frontend
        run: npm ci && npm run gen:api
      - name: Generate Pydantic models
        run: pip install datamodel-code-generator && python -m datamodel_code_generator --input spec/openapi/openapi.json --input-file-type openapi --output-model-type pydantic_v2.BaseModel --openapi-scopes schemas api --output backend/app/generated/models.py
      - name: Fail on drift
        run: git diff --exit-code
```

The `backend`/`frontend` jobs keep running unchanged; they consume the committed
artifacts.

---

## 5. Pitfalls

1. **Tool versions must be pinned.**
   - TypeSpec: keep `@typespec/compiler` and `@typespec/openapi3` on matching
     versions. `@typespec/openapi3` 1.x is current (1.17.0 at research time);
     a pre-0.67 release had a hard minimum Node 20 — irrelevant here but shows
     version drift is real.
   - hey-api `@hey-api/openapi-ts` is **0.x** — pin exact (`-E`), read migration
     notes on upgrade.
   - `datamodel-code-generator`'s FastAPI *server* generation is experimental;
     pin the version and prefer models-only.

2. **`tsp` CLI availability.** `tsp` is not on PATH by default; invoke it via a
   pinned devDependency (`npx tsp compile .`) or a local install so the version is
   reproducible. The CI contract job uses Node 22, so `npx` works there.

3. **OpenAPI dialect.** Emit **3.1 JSON**, not YAML/3.0, to maximise downstream
   support; both hey-api and datamodel-code-generator handle 3.1.

4. **Multi-page Vite build.** The generated client lives under `src/` and is
   imported as a library — it is **not** a new HTML entry. Do **not** touch
   `build.rollupOptions.input` in `frontend/vite.config.ts` (currently `home`,
   `booking`, `admin`); adding a stray entry there is a known footgun noted in
   `AGENTS.md`.

5. **`frontend/package-lock.json` must stay in sync with `npm ci`.** CI runs
   `npm ci`, which fails if `package.json` and the lock file disagree. Adding
   `@hey-api/openapi-ts` / `@hey-api/client-fetch` requires a lock-file update
   committed in the **same** PR. Since **npm is not installed locally**, either
   regenerate the lock on a machine with Node 22, or let CI/`npm install` produce
   it — but the commit must include the refreshed `package-lock.json` or CI breaks.

6. **Generated code ownership.** Everything under `*/generated/` and
   `spec/openapi/` is machine-written and overwritten on every run — never
   hand-edit; put any customisation in the emitters/generators or in hand-written
   wrappers around the generated code.

7. **Contract drift.** Because artifacts are committed, a spec change that isn't
   regenerated will silently pass CI. The `git diff --exit-code` drift check in
   the contract job is the guard.

---

## Recommendation summary

- **Contract source:** TypeSpec in `spec/` (`main.tsp`, `tspconfig.yaml`,
  pinned `package.json`), using `@typespec/http` + `@typespec/versioning`.
- **OpenAPI emitter:** `@typespec/openapi3` → OpenAPI **3.1 JSON** at
  `spec/openapi/openapi.json`.
- **TS SDK generator:** **`@hey-api/openapi-ts` + `@hey-api/client-fetch`**
  (orval's React hooks are irrelevant for vanilla TS; `openapi-typescript` /
  `openapi-fetch` are in maintenance mode as of Sep 2026). Output to
  `frontend/src/api/generated/`, consumed by `frontend/src/api.ts`.
- **Backend generator:** **`datamodel-code-generator`**, models-only
  (`pydantic_v2.BaseModel`), output to `backend/app/generated/models.py`; keep
  FastAPI routers hand-written (server generation is experimental).
- **Repo layout:** `spec/` for sources, `spec/openapi/` + `*/generated/` committed,
  guarded by a CI drift check.
- **CI:** add a `contract` job to `.github/workflows/ci.yml` that emits OpenAPI,
  regenerates the TS client and Pydantic models, and fails on `git diff`.

## Sources

- TypeSpec Models — https://typespec.io/docs/language-basics/models/
- TypeSpec REST getting started — https://typespec.io/docs/getting-started/getting-started-rest/01-setup-basic-syntax/
- TypeSpec Operations & Responses — https://typespec.io/docs/getting-started/getting-started-rest/02-operations-responses/
- TypeSpec Versioning — https://typespec.io/docs/getting-started/getting-started-rest/06-versioning/
- TypeSpec CLI — https://typespec.io/docs/handbook/cli/
- `@typespec/openapi3` README — https://github.com/microsoft/typespec/blob/main/packages/openapi3/README.md
- `@typespec/openapi3` emitter reference — https://typespec.io/docs/emitters/openapi3/reference/emitter/
- OpenAPI v3 emitter guide — https://typespec.io/docs/emitters/openapi3/openapi/
- `@hey-api/openapi-ts` get started — https://heyapi.dev/docs/openapi/typescript/get-started
- openapi-typescript 2026 roadmap (openapi-fetch maintenance) — https://github.com/openapi-ts/openapi-typescript/discussions/2559
- openapi-typescript maintenance mode (Sep 2026) — https://github.com/openapi-ts/openapi-typescript/issues/2874
- TS SDK generator comparison — https://www.speakeasy.com/docs/sdks/languages/typescript/oss-comparison-ts
- `datamodel-code-generator` repo — https://github.com/koxudaxi/datamodel-code-generator/
- `datamodel-code-generator` target options (server/client, experimental) — https://datamodel-code-generator.koxudaxi.dev/cli-reference/target-generation-options/
- `datamodel-code-generator` fastapi-code-generator migration — https://datamodel-code-generator.koxudaxi.dev/fastapi-code-generator-migration/
- `fastapi-code-generator` repo — https://github.com/koxudaxi/fastapi-code-generator
- `openapi-python-client` repo — https://github.com/openapi-generators/openapi-python-client/
