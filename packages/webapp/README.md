# MiraLingo Web App

MiraLingo is the local web application shell for learning Mirad. The S01 slice provides a visible logged-out welcome page, an explicit local-development admin login path, and diagnostic auth state endpoints that downstream slices can reuse.

## Current Scope

Implemented in this package:

- FastAPI backend with `/health`, `/auth/current-user`, `/auth/login`, and `/auth/logout` endpoints.
- Signed-cookie session state that stores only password-free user fields.
- Guarded local admin bootstrap (`admin` / `admin`) that works only when development settings enable it.
- Svelte welcome screen for anonymous users and app home for the local admin session.

Future slices will add Mirad pronunciation, translation, vocabulary, and progress workflows using the engines in sibling packages.

## Local Configuration

The backend reads these environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MIRALINGO_ENV` | `development` | Runtime environment. Local admin login is refused unless this is `development`. |
| `MIRALINGO_ENABLE_LOCAL_ADMIN` | `true` | Enables the development-only `admin` / `admin` bootstrap when truthy. |
| `MIRALINGO_SESSION_SECRET` | `miralingo-dev-session-secret` | Secret used to sign session cookies. Override outside throwaway local runs. |

Local admin bootstrap is intentionally unsuitable for production. A production-like run should set `MIRALINGO_ENV=production`, which returns a structured `local_admin_disabled` response for `/auth/login` even if the username and password are correct.

## Backend Startup

From the repository root:

```bash
PYTHONPATH=packages/webapp/src \
  MIRALINGO_ENV=development \
  MIRALINGO_ENABLE_LOCAL_ADMIN=true \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src
```

Useful backend checks:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/auth/current-user
curl -i -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}'
```

The logged-out current-user response is expected to be HTTP 401 with an explicit JSON body, not a server failure.

## Frontend Startup

The Svelte frontend lives in `packages/webapp/frontend`.

```bash
cd packages/webapp/frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open the Vite URL shown by the command. When logged out, the page should show "Welcome to MiraLingo" and the local admin login card. After signing in as `admin` / `admin` against a development backend, it should show the MiraLingo app home.

## S02 Card Content Import Preview

S02 adds a deterministic, non-mutating MiraLingo card content import preview. It imports public learning content from two local sources:

- **Phrase cards:** the configured CSV at `MIRALINGO_PHRASE_CSV_PATH`, defaulting to `data/phrases/english-mirad-sentence-pairs.csv`. Rows must provide `english` and `mirad`; only multi-word English phrases with non-empty Mirad text become phrase cards.
- **Word cards:** a bounded default word-candidate stream looked up through the Mirad translator lexicon. The default preview inspects at most 500 candidates, and callers may lower or raise the bound from 0 to 5000.

The CLI prints deterministic JSON counts and stacktrace-free diagnostics:

```bash
PYTHONPATH=packages/webapp/src:packages/translator/src \
  python -m mirad_webapp.content_cli --word-limit 500
```

Use `--phrase-csv PATH` to override the configured phrase source for local inspection, and `--include-cards` to include imported card rows in addition to counts. The installed script entry point is `miralingo-content-import`.

The API exposes the same preview through `GET /content/import/preview`:

```bash
curl -s 'http://127.0.0.1:8000/content/import/preview?word_limit=500'
```

The endpoint is intentionally non-mutating, does not require auth, and does not accept request-controlled file paths. The only source selector is `source=configured`, and `word_limit` is validated from 0 through 5000.

Successful CLI/API payloads include:

| Field | Purpose |
|---|---|
| `ok` | `true` for a completed preview. |
| `mutating` | Always `false`; S02 does not persist user progress or card state. |
| `cards` | Imported card rows when included by the surface; API includes them, CLI omits them unless `--include-cards` is passed. |
| `counts.phrase.imported` | Phrase cards accepted from the CSV. |
| `counts.phrase.skipped.blank_english` | CSV rows skipped because English text is blank. |
| `counts.phrase.skipped.blank_mirad` | CSV rows skipped because Mirad text is blank. |
| `counts.phrase.skipped.malformed_row` | CSV rows skipped because extra columns made the row malformed. |
| `counts.phrase.skipped.one_word_english` | CSV rows skipped because English has fewer than two word tokens. |
| `counts.phrase.duplicate` | Phrase rows suppressed because the normalized English/Mirad pair was already imported. |
| `counts.phrase.source_error` | Phrase source failures counted before returning a structured error. |
| `counts.word.imported` | Word cards accepted after lexicon lookup. |
| `counts.word.missed.lexicon_miss` | Word candidates with no Mirad lexicon hit. |
| `counts.word.duplicate` | Word rows suppressed because the normalized English/Mirad pair was already imported. |
| `counts.word.source_error` | Word provider or lexicon failures counted before returning a structured error. |
| `sources.phrase_csv` | Phrase CSV path used by the preview. |

Failure payloads keep diagnostics explicit without stacktrace parsing. Missing phrase sources return `error: source_missing`, `phase: phrase_import`, `source_type: phrase_csv`, and `source_path`. Invalid CLI limits return `error: invalid_word_limit` and `phase: argument_validation`; invalid API limits or source tampering return FastAPI HTTP 422 validation errors.

## Verification

Run the full deterministic webapp regression from the repository root:

```bash
PYTHONPATH=packages/webapp/src:packages/translator/src python -m pytest packages/webapp/tests -q
```

This verifies the S01 auth/app shell contracts plus the S02 importer, CLI, and API preview contracts.

The S01 flow coverage in `packages/webapp/tests/test_s01_flow.py` verifies:

1. `/health` is available and `/auth/current-user` distinguishes the logged-out state with HTTP 401 JSON.
2. The checked-in Svelte app contains the logged-out welcome and login surfaces.
3. Development local admin login succeeds and `/auth/current-user` reports the admin session.
4. Logout returns the client to the logged-out state.
5. Production settings refuse the local admin bootstrap without echoing credentials.
6. Malformed login bodies fail validation without creating a session.

## Failure Modes

- **Backend process unavailable:** browser fetches fail and the frontend shows "Could not reach MiraLingo auth. Check that the web server is running." The deterministic pytest path avoids network dependency by using FastAPI `TestClient` in process.
- **Logged-out session:** `/auth/current-user` returns HTTP 401 with `{ "authenticated": false, "user": null }`, allowing agents and UI code to distinguish anonymous state from backend failure.
- **Invalid credentials:** `/auth/login` returns HTTP 401 with `error: invalid_credentials` and does not echo the submitted password.
- **Local admin disabled or non-development environment:** `/auth/login` returns HTTP 403 with `error: local_admin_disabled`.
- **Malformed JSON/body:** FastAPI validation returns HTTP 422 and no session is created.
- **Frontend source missing during tests:** the S01 flow test fails at file read/assertion time, surfacing a broken or moved UI contract.

## Load Profile

S01 authentication is a local development bootstrap backed by signed cookies and in-process request handling. The expected load is one local developer browser session; at 10x, CPU/request concurrency in the ASGI server would saturate before any database, network API, or subprocess because none are used by this flow. Protection is intentionally minimal for this non-production bootstrap: production-like environments disable the admin bootstrap, and future real auth should add rate limiting and persistent identity storage before accepting public traffic.

## Negative Tests

Negative coverage lives in `packages/webapp/tests/test_auth.py` and `packages/webapp/tests/test_s01_flow.py`:

- Invalid `admin` password returns `invalid_credentials` without password echo.
- Logged-out `/auth/current-user` returns explicit HTTP 401 JSON.
- Production environment refuses `admin` / `admin` with `local_admin_disabled`.
- Logout clears the authenticated session.
- Malformed login body returns HTTP 422 and leaves the session anonymous.
