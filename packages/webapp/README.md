# MiraLingo Web App

MiraLingo is the local web application shell for learning Mirad. The S01 slice provides a visible logged-out welcome page, an explicit local-development admin login path, and diagnostic auth state endpoints that downstream slices can reuse.

## Current Scope

Implemented in this package:

- FastAPI backend with `/health`, `/auth/current-user`, `/auth/login`, and `/auth/logout` endpoints.
- Signed-cookie session state that stores only password-free current-user identity; learner accounts, shown cards, and answer events are persisted in SQLite.
- Guarded local admin bootstrap (`admin` / `admin`) that works only when development settings enable it.
- Authenticated adaptive practice APIs at `/practice/queue` and `/practice/answers`.
- Authenticated MBROLA-backed Mirad answer audio at `/practice/audio/{card_id}` with structured unavailable diagnostics.
- Svelte welcome screen for anonymous users and an authenticated practice panel for the local admin session.

Future slices will add richer Mirad pronunciation, translation, vocabulary, and progress workflows using the engines in sibling packages.

## Local Configuration

The backend reads these environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `MIRALINGO_ENV` | `development` | Runtime environment. Local admin login is refused unless this is `development`. |
| `MIRALINGO_ENABLE_LOCAL_ADMIN` | `true` | Enables the development-only `admin` / `admin` bootstrap when truthy. |
| `MIRALINGO_SESSION_SECRET` | `miralingo-dev-session-secret` | Secret used to sign session cookies. Override outside throwaway local runs. |
| `MIRALINGO_DATABASE_PATH` | `.miralingo/miralingo.sqlite3` | SQLite database path for durable learner accounts, shown cards, and answer events. Parent directories are created at startup. |
| `MIRALINGO_PHRASE_CSV_PATH` | `data/phrases/english-mirad-sentence-pairs.csv` | Phrase card source used together with real wordfreq-ranked word cards. |

Local admin bootstrap is intentionally unsuitable for production. A production-like run should set `MIRALINGO_ENV=production`, which returns a structured `local_admin_disabled` response for `/auth/login` even if the username and password are correct.

## S08 SQLite Persistence and Wordfreq Cards

S08 replaces the temporary practice/session stores with a SQLite-backed storage boundary and real ranked word-card sourcing. The default database path is controlled by `MIRALINGO_DATABASE_PATH`; if the variable is omitted, the backend creates `.miralingo/miralingo.sqlite3` relative to the process working directory. Use a throwaway path such as `/tmp/miralingo-dev.sqlite3` when reproducing persistence bugs so browser sessions and test runs do not share state accidentally.

Signed cookies are intentionally small: they store only the current password-free user identity needed to authenticate a request. They do **not** store password hashes, salts, shown-card history, answer events, or submitted practice answers. Registered learner credentials and practice history live in SQLite instead.

Word cards are generated from the real `wordfreq` dependency (`wordfreq.top_n_list('en', ...)`) and then filtered through the Mirad translator lexicon. Phrase cards still come from `MIRALINGO_PHRASE_CSV_PATH`. If word cards are missing, first verify that `wordfreq` is installed in the active webapp environment and that `packages/translator/src` is present on `PYTHONPATH` for local source runs.

Safe SQLite inspection surfaces for future agents:

| Table | Safe fields to inspect | Secret caution |
|---|---|---|
| `users` | `username`, `role`, `created_at` | Do not print or copy `salt` or `password_hash`. |
| `shown_cards` | `username`, `card_id`, `base_card_id`, `direction`, `card_type`, `prompt_language`, `answer_language`, `shown_at` | Contains no credentials. |
| `answer_events` | `username`, `card_id`, `base_card_id`, `direction`, `card_type`, `submitted_answer`, `expected_answer`, `correct`, `answered_at` | Contains learner-submitted answers but no passwords, salts, or hashes. |

Example local diagnostics from the repository root:

```bash
MIRALINGO_DATABASE_PATH=/tmp/miralingo-dev.sqlite3 \
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src

python - <<'PY'
import sqlite3
from pathlib import Path
path = Path('/tmp/miralingo-dev.sqlite3')
with sqlite3.connect(path) as db:
    for table in ('users', 'shown_cards', 'answer_events'):
        count = db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        print(f'{table}: {count}')
    print(db.execute('SELECT username, card_id, direction, card_type, shown_at FROM shown_cards ORDER BY id DESC LIMIT 5').fetchall())
    print(db.execute('SELECT username, card_id, correct, answered_at FROM answer_events ORDER BY id DESC LIMIT 5').fetchall())
PY
```

Storage failures are returned as stacktrace-free JSON with stable `phase` values such as `storage_init`, `auth_register`, `auth_login`, `practice_queue`, `practice_answer`, and `practice_progress`. These payloads must not include submitted passwords, password hashes, or salts.

## Backend Startup

From the repository root:

```bash
PYTHONPATH=packages/webapp/src:packages/translator/src:packages/tts/src:src \
  MIRALINGO_ENV=development \
  MIRALINGO_ENABLE_LOCAL_ADMIN=true \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src
```

## One-command local startup (recommended)

Use the root launcher script to avoid Python path drift and frontend/backend mismatch:

```bash
./scripts/start_miralingo.sh
```

This script:
- ensures frontend dependencies are installed,
- starts backend with the required package paths (`webapp`, `translator`, `tts`, and root `src`),
- starts frontend on port `5173`,
- prints stable URLs for manual testing,
- shuts both down cleanly on `Ctrl+C`.

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

Open the Vite URL shown by the command. When logged out, the page should show "Welcome to MiraLingo" and the local admin login card. After signing in as `admin` / `admin` against a development backend, it should show the MiraLingo app home and authenticated practice panel.

## S03 Adaptive Practice Queue

S03 adds a session-scoped adaptive practice loop for logged-in users. The frontend fetches one bounded queue at a time from `GET /practice/queue?limit=3`; it does not poll. From the dashboard, users click **Continue Practice** to enter focused study mode. The current card shows the prompt, typed-answer input, optional Mirad answer reveal, and card diagnostics. **Submit answer** posts typed responses to `POST /practice/answers`; **Show answer** records a miss/reveal path, and controls are disabled while requests are in flight to avoid duplicate events.

Useful authenticated API checks after logging in with a cookie jar:

```bash
curl -c /tmp/miralingo.cookies -b /tmp/miralingo.cookies \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' \
  http://127.0.0.1:8000/auth/login
curl -b /tmp/miralingo.cookies 'http://127.0.0.1:8000/practice/queue?limit=3'
curl -b /tmp/miralingo.cookies -H 'Content-Type: application/json' \
  -d '{"card_id":"word:the","correct":false}' \
  http://127.0.0.1:8000/practice/answers
```

Practice responses are deliberately diagnostic. Queue payloads include `ok`, `phase`, `event_count`, `cards[].scheduler_reason`, `cards[].mastery`, and `cards[].recency`. Answer payloads include `ok`, `phase`, `card_id`, `card_type`, `correct`, `event_count`, `scheduler_reason`, `mastery`, `recency`, and `latest_event`. Error paths return structured phases for unauthenticated, missing-content, invalid-payload, and unknown-card cases without echoing credentials.

## S04 Mirad Answer Audio Diagnostics

S04 adds an authenticated card-bound audio endpoint for MiraLingo practice cards:

```text
GET /practice/audio/{card_id}
```

The endpoint accepts only a stable practice `card_id` from configured card content, resolves that card server-side, and synthesizes the card's Mirad answer. It never accepts arbitrary text, client-selected output paths, or request-controlled filesystem paths. The frontend speaker control requests this endpoint only after the user clicks **Hear Mirad answer** on the current card.

Successful responses are raw WAV audio:

| Signal | Expected value |
|---|---|
| HTTP status | `200` |
| `Content-Type` | `audio/wav` |
| `Cache-Control` | `no-store` |
| `X-MiraLingo-Audio-Phase` | `audio_synthesis` |
| `X-MiraLingo-Audio-Backend` | `mbrola` |
| `X-MiraLingo-Card-Id` | Requested stable card id |

Unavailable and error responses are JSON and are intentionally distinct so operators can tell dependency problems from auth/content/card problems:

| HTTP status | `error` | Meaning | Operator action |
|---|---|---|---|
| `401` | `unauthenticated` | No active session cookie. | Log in again; do not troubleshoot MBROLA first. |
| `404` | `source_missing` | Configured phrase CSV/content source is missing. | Check `MIRALINGO_PHRASE_CSV_PATH` or the default data file. |
| `404` | `unknown_card` | The requested card is not in the configured practice content. | Refresh the queue and verify card import output. |
| `422` | `invalid_card_id` | Card id is blank or path-like. | Use a stable id from `/practice/queue`; do not pass paths. |
| `422` | `invalid_card_payload` | The card has no Mirad answer to synthesize. | Fix card import/content data. |
| `503` | `audio_backend_unavailable` | The Python MBROLA backend import failed. | Verify `packages/tts/src` is on `PYTHONPATH` or the package is installed. |
| `503` | `mbrola_unavailable` | The `mbrola` binary is missing from `PATH`. | Install MBROLA locally. |
| `503` | `mbrola_voice_unavailable` | The `de6` voice database is missing. | Install the `de6` MBROLA voice package. |
| `502` | `audio_synthesis_failed` | MBROLA was present but synthesis failed. | Inspect the `detail` field for the safe exception summary. |

All JSON audio failures include `ok: false`, `phase: audio_synthesis`, `backend: mbrola`, `card_id`, and a stacktrace-free `detail`. They must not return credentials.

Local Debian/Ubuntu MBROLA setup for real audio playback:

```bash
sudo apt install mbrola mbrola-de6
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src \
  MIRALINGO_ENV=development \
  MIRALINGO_ENABLE_LOCAL_ADMIN=true \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src
```

Useful authenticated inspection flow:

```bash
curl -c /tmp/miralingo.cookies -b /tmp/miralingo.cookies \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' \
  http://127.0.0.1:8000/auth/login
curl -i -b /tmp/miralingo.cookies \
  -H 'Accept: audio/wav, application/json' \
  http://127.0.0.1:8000/practice/audio/phrase:hello-world
```

CI and deterministic pytest coverage mock the MBROLA backend. The focused audio tests verify WAV success headers plus negative states for missing binary, missing `de6` voice, backend import failure, unknown card, invalid/path-like ids, missing content source, authentication failure, and synthesis failure without requiring a system MBROLA install.

## S05 Final Runtime UAT Flow

Use this end-to-end flow to prove the logged-out welcome, local admin login, mixed word/phrase practice, audio diagnostics, and progress statistics still work together after code changes.

### 1. Start the backend

From the repository root, include all package sources used by the web app, TTS backend, and translator-backed word cards:

```bash
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src \
  MIRALINGO_ENV=development \
  MIRALINGO_ENABLE_LOCAL_ADMIN=true \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src
```

The backend should listen on `http://127.0.0.1:8000`. If audio playback is required rather than diagnostics-only UAT, install the local MBROLA runtime and `de6` voice before starting the server. Missing MBROLA or `de6` is acceptable for local smoke testing only when the API/UI show the structured unavailable diagnostic described in the S04 table.

### 2. Start the Svelte frontend

In a second shell from the repository root, install dependencies from the checked-in lockfile only if `packages/webapp/frontend/node_modules` is absent, then start Vite:

```bash
if [ ! -d packages/webapp/frontend/node_modules ]; then
  npm install --prefix packages/webapp/frontend
fi
npm --prefix packages/webapp/frontend run dev -- --host 127.0.0.1
```

Do not commit `node_modules`. Open the Vite URL, normally `http://127.0.0.1:5173`, and confirm:

1. Logged-out visitors see **Welcome to MiraLingo** and the local admin login card.
2. Signing in as `admin` / `admin` succeeds only in development mode and clears the password field.
3. The authenticated panel shows a mixed practice queue with both `word` and `phrase` card types when the configured content source is available.
4. Click **Continue Practice** to enter focused study mode, then use **Submit answer** (typed response) or **Show answer** (reveal/miss path); actions disable while in flight, refresh the queue, and update session progress without polling.
5. **Hear Mirad answer** either plays a WAV response or shows a structured unavailable diagnostic such as `mbrola_unavailable` or `mbrola_voice_unavailable`; those diagnostics indicate local runtime setup, not an app failure.
6. **Practice stats** changes after submitted answers, including attempts, correct/incorrect counts, accuracy, per-type summaries, latest answer, and weak/mastered/new/stale badges.
7. Logging out returns to the welcome screen and removes practice/progress/audio state.

### 3. Inspect authenticated APIs with a cookie jar

```bash
curl -c /tmp/miralingo.cookies -b /tmp/miralingo.cookies \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' \
  http://127.0.0.1:8000/auth/login

curl -b /tmp/miralingo.cookies \
  'http://127.0.0.1:8000/practice/queue?limit=4'

curl -b /tmp/miralingo.cookies \
  -H 'Content-Type: application/json' \
  -d '{"card_id":"phrase:hello-world","correct":true}' \
  http://127.0.0.1:8000/practice/answers

curl -b /tmp/miralingo.cookies \
  -H 'Content-Type: application/json' \
  -d '{"card_id":"word:the","correct":false}' \
  http://127.0.0.1:8000/practice/answers

curl -b /tmp/miralingo.cookies \
  http://127.0.0.1:8000/practice/progress

curl -i -b /tmp/miralingo.cookies \
  -H 'Accept: audio/wav, application/json' \
  http://127.0.0.1:8000/practice/audio/phrase:hello-world
```

A successful `/practice/progress` payload has `ok: true`, `phase: practice_progress`, `event_count`, `total`, `correct`, `incorrect`, `accuracy`, `per_card`, `per_type`, `latest_event`, `weak_count`, `mastered_count`, `stale_count`, and `new_count`. `per_type` contains `word` and `phrase` summaries with `attempts`, `correct`, `incorrect`, and `accuracy`; `per_card` entries expose each card id/type plus attempts, correctness totals, accuracy, latest event metadata, and scheduler state. Logged-out progress requests return `401` with `error: unauthenticated` and `phase: practice_progress`.

### 4. Final verification commands

Run deterministic tests and the production frontend build from the repository root:

```bash
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src python -m pytest packages/webapp/tests -q
npm --prefix packages/webapp/frontend run build
```

The pytest regression covers unauthenticated progress/audio, development-only admin login, production refusal of local admin, missing audio runtime diagnostics, missing content source diagnostics, mixed practice events, and the static progress/audio UI contracts. The production build proves the Svelte entrypoint compiles without depending on the Vite dev server.

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
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src python -m pytest packages/webapp/tests -q
```

This verifies the S01 auth/app shell contracts, S02 importer/CLI/API preview contracts, S03 authenticated adaptive practice API/frontend source contracts, and S04 authenticated MBROLA audio API/frontend diagnostics. Audio tests mock synthesis, so this command does not require a local `mbrola` binary or `de6` voice package.

The S01 flow coverage in `packages/webapp/tests/test_s01_flow.py` verifies:

1. `/health` is available and `/auth/current-user` distinguishes the logged-out state with HTTP 401 JSON.
2. The checked-in Svelte app contains the logged-out welcome and login surfaces.
3. Development local admin login succeeds and `/auth/current-user` reports the admin session.
4. Logout returns the client to the logged-out state.
5. Production settings refuse the local admin bootstrap without echoing credentials.
6. Malformed login bodies fail validation without creating a session.

## Failure Modes

- **Audio backend import unavailable:** `/practice/audio/{card_id}` returns JSON with `error: audio_backend_unavailable`, `phase: audio_synthesis`, `backend: mbrola`, and the card id; run with `packages/tts/src` on `PYTHONPATH` or install the TTS package.
- **MBROLA binary missing:** authenticated audio returns HTTP 503 with `error: mbrola_unavailable`; install `mbrola` and verify it is on `PATH`.
- **MBROLA de6 voice missing:** authenticated audio returns HTTP 503 with `error: mbrola_voice_unavailable`; install the `mbrola-de6` package and verify `/usr/share/mbrola/de6/de6` exists.
- **MBROLA synthesis failure:** authenticated audio returns HTTP 502 with `error: audio_synthesis_failed` and safe diagnostic detail, not a traceback.
- **Audio card/content/auth errors:** unauthenticated audio is `401 unauthenticated`, missing phrase CSV is `404 source_missing`, unknown card ids are `404 unknown_card`, and blank/path-like card ids are `422 invalid_card_id`; these are not MBROLA install problems.
- **Practice API unavailable or answer rejected:** the authenticated practice panel shows an actionable alert and avoids exposing credentials or raw stack traces.
- **Practice content missing or empty:** queue errors mention content configuration; empty queues show that cards must be imported first.
- **Repeated answer clicks:** practice answer buttons are disabled while submission is in flight, preventing duplicate events for the same click.
- **Backend process unavailable:** browser fetches fail and the frontend shows "Could not reach MiraLingo auth. Check that the web server is running." The deterministic pytest path avoids network dependency by using FastAPI `TestClient` in process.
- **Logged-out session:** `/auth/current-user` returns HTTP 401 with `{ "authenticated": false, "user": null }`, allowing agents and UI code to distinguish anonymous state from backend failure.
- **Invalid credentials:** `/auth/login` returns HTTP 401 with `error: invalid_credentials` and does not echo the submitted password.
- **Local admin disabled or non-development environment:** `/auth/login` returns HTTP 403 with `error: local_admin_disabled`.
- **Malformed JSON/body:** FastAPI validation returns HTTP 422 and no session is created.
- **Frontend source missing during tests:** the S01 flow test fails at file read/assertion time, surfacing a broken or moved UI contract.

## Load Profile

S01 authentication is a local development bootstrap backed by signed cookies and in-process request handling. The expected load is one local developer browser session; at 10x, CPU/request concurrency in the ASGI server would saturate before any database, network API, or subprocess because none are used by this flow. Protection is intentionally minimal for this non-production bootstrap: production-like environments disable the admin bootstrap, and future real auth should add rate limiting and persistent identity storage before accepting public traffic.

## Negative Tests

Negative coverage lives in `packages/webapp/tests/test_auth.py`, `packages/webapp/tests/test_s01_flow.py`, `packages/webapp/tests/test_s03_flow.py`, `packages/webapp/tests/test_audio_api.py`, and `packages/webapp/tests/test_audio_ui_static.py`:

- Invalid `admin` password returns `invalid_credentials` without password echo.
- Logged-out `/auth/current-user` returns explicit HTTP 401 JSON.
- Production environment refuses `admin` / `admin` with `local_admin_disabled`.
- Logout clears the authenticated session.
- Malformed login body returns HTTP 422 and leaves the session anonymous.
- Practice queue and answer submission require auth and return structured unauthenticated diagnostics.
- Unknown practice cards return structured `unknown_card` diagnostics without credential echo.
- Audio API success tests assert authenticated `audio/wav` responses, no-store caching, and `X-MiraLingo-Audio-*` headers with mocked MBROLA synthesis.
- Audio API negative tests distinguish unauthenticated sessions, unknown cards, missing content source, backend import failure, missing `mbrola` binary, missing `de6` voice, synthesis failure, and invalid/path-like card ids.
- Audio frontend static tests assert the speaker control is accessible, requests the encoded card-bound endpoint, handles JSON unavailable/error payloads visibly, revokes stale blob URLs, and resets audio state on queue refresh, card change, and logout.
