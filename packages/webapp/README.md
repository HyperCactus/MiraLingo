# MiraLingo Web App

**MiraLingo** is an interactive web application for learning the Mirad constructed language through adaptive spaced repetition. It presents vocabulary cards in two directions (English→Mirad and Mirad→English), tracks your accuracy and streaks, and promotes cards to "mastered" status as you improve.

## How It Works

### Adaptive Practice Loop

MiraLingo uses a **direction-aware adaptive scheduler** that treats each vocabulary card as two separate practice items — one for each translation direction. For example, the word "the" (Mirad: "te") creates two cards:

- **English→Mirad**: shown "the", answer "te"
- **Mirad→English**: shown "te", answer "the"

The scheduler ranks all cards by learning state (new → weak → stale review → mastered review) and interleaves cards to avoid seeing the same word in both directions back-to-back. Cards you struggle with appear more frequently; cards you've mastered appear less often.

**Mastery criteria:** A card is marked *mastered* when you answer it correctly 3 times in a row **and** maintain an accuracy of at least 80%. Mastered cards still appear for periodic review if they go stale (unused for 14 days).

### Practice Modes

| Mode | Active cards | Focus |
|------|-------------|-------|
| **Mixed** (default) | 8 | Balanced mix of new, weak, and review cards |
| **Build Vocabulary** | 12 | Heavier on new cards to expand your vocabulary |
| **Revision** | All seen | Only cards you've already encountered, prioritizing weak and stale ones |

### Achievements

MiraLingo awards achievement milestones when you master your 1st, 10th, 20th, 50th, 80th, and 100th direction-card. An achievement toast appears with a trophy emoji and the card you just mastered. The toast can be dismissed with the × button or by continuing to the next card.

### Keyboard Navigation

The practice flow is fully keyboard-driven:

- **Type your answer** → press Enter to submit
- **After reveal/feedback** → press Enter to continue to the next card
- The answer input auto-focuses when each new card appears

### Audio

When MBROLA with the `de6` voice is installed, MiraLingo can pronounce Mirad answers aloud. Click the speaker button on any card with a Mirad answer to hear it. If the audio backend is unavailable, a structured diagnostic message is shown instead of broken audio.

---

## Architecture

### Backend (FastAPI)

- **`/auth/login`**, **`/auth/logout`**, **`/auth/current-user`** — Signed-cookie session auth with development-only admin bootstrap (`admin` / `admin`)
- **`/practice/queue`** — Returns a bounded adaptive practice queue (direction-aware cards, scheduler diagnostics)
- **`/practice/answers`** — Records a submitted answer, updates mastery/recency state, computes achievement milestones
- **`/practice/progress`** — Returns per-card and per-type progress statistics including mastery, accuracy, and scheduler reasons
- **`/practice/audio/{card_id}`** — Synthesizes Mirad answer audio via MBROLA; returns WAV or structured JSON diagnostics
- **`/settings`** — Authenticated user preferences (theme, sound effects mode, TTS speed)
- **`/content/import/preview`** — Non-mutating preview of card content from phrase CSV and wordfreq-ranked word cards

All practice endpoints require authentication. Logged-out requests return HTTP 401 JSON.

### Frontend (Svelte 5 + Vite)

- **Welcome page** — logged-out landing with local dev login
- **Dashboard** — practice statistics, progress overview, settings
- **Practice card** — typed-answer recall with reveal/continue flow, achievement toasts, keyboard navigation
- **Lexicon panel** — inline word lookup during practice
- **Dark/light theme** — respects system preference, override in settings

### Persistence

SQLite stores user accounts, practice events (answer history), card lifecycle state (new → active → mastered), and user settings. The default database is `.miralingo/miralingo.sqlite3`. Signed cookies contain only the username — no passwords or hashes in cookies.

---

## Local Development

### One-command startup (recommended)

```bash
./scripts/start_miralingo.sh
```

This starts both backend (port 8000) and frontend (port 5173) with correct `PYTHONPATH`, installs frontend deps if needed, and prints URLs. Press `Ctrl+C` to stop both.

### Manual startup

Backend:

```bash
PYTHONPATH=packages/webapp/src:packages/translator/src:packages/tts/src:src \
  MIRALINGO_ENV=development \
  MIRALINGO_ENABLE_LOCAL_ADMIN=true \
  python -m uvicorn mirad_webapp.api:app --reload --app-dir packages/webapp/src
```

Frontend (separate shell):

```bash
cd packages/webapp/frontend
npm install  # first time only
npm run dev -- --host 127.0.0.1
```

### Audio setup (optional, for Mirad pronunciation)

```bash
sudo apt install mbrola mbrola-de6
```

Without MBROLA, the audio button shows a diagnostic instead of playing sound — everything else works normally.

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `MIRALINGO_ENV` | `development` | Runtime environment. Local admin login requires `development`. |
| `MIRALINGO_ENABLE_LOCAL_ADMIN` | `true` | Enables the `admin` / `admin` bootstrap. Override in production. |
| `MIRALINGO_SESSION_SECRET` | `miralingo-dev-session-secret` | Secret for signing session cookies. Override outside throwaway runs. |
| `MIRALINGO_DATABASE_PATH` | `.miralingo/miralingo.sqlite3` | SQLite database path. Parent directories are created at startup. |
| `MIRALINGO_PHRASE_CSV_PATH` | `data/phrases/english-mirad-sentence-pairs.csv` | Phrase card source. |

---

## API Examples

```bash
# Login (saves cookie)
curl -c /tmp/ml.cookies -b /tmp/ml.cookies \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin"}' \
  http://127.0.0.1:8000/auth/login

# Get practice queue
curl -b /tmp/ml.cookies 'http://127.0.0.1:8000/practice/queue?limit=8'

# Submit an answer
curl -b /tmp/ml.cookies -H 'Content-Type: application/json' \
  -d '{"card_id":"word:the#english-to-mirad","answer":"te"}' \
  http://127.0.0.1:8000/practice/answers

# Get progress stats
curl -b /tmp/ml.cookies http://127.0.0.1:8000/practice/progress

# Get Mirad audio for a card
curl -b /tmp/ml.cookies \
  -H 'Accept: audio/wav, application/json' \
  http://127.0.0.1:8000/practice/audio/word:the
```

---

## Practice Scheduling Details

The scheduler in `practice_engine.py` handles:

- **Direction-balancing**: Each base word generates two direction-cards (En→Mir and Mir→En). The scheduler avoids showing both directions of the same word consecutively.
- **Adaptive ranking**: Cards are ranked by learning state — new items, weak items (accuracy below 80%), stale mastered reviews, and recent mastered cards — with session-struggling detection that biases toward review over new material.
- **Mastery promotion**: A card is promoted to "mastered" when it has ≥3 consecutive correct answers and overall accuracy of at least 80%. Mastered cards still appear for stale review after 14 days of inactivity.
- **Achievement milestones**: The first time one or more direction-cards are mastered, an achievement payload is returned with the answer response. Thresholds are at 1, 10, 20, 50, 80, and 100 mastered cards.

---

## Verification

Run the full deterministic test suite from the repository root:

```bash
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src python -m pytest packages/webapp/tests -q
```

This covers auth flows, practice API contracts, adaptive scheduling, achievement milestones, audio diagnostics, and Svelte source assertions — all without requiring MBROLA or a running server.

Build the production frontend:

```bash
npm --prefix packages/webapp/frontend run build
```

---

## Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Audio returns `audio_backend_unavailable` | TTS package not on PYTHONPATH | Add `packages/tts/src` to `PYTHONPATH` or `pip install -e packages/tts/` |
| Audio returns `mbrola_unavailable` | `mbrola` binary not on PATH | `sudo apt install mbrola` |
| Audio returns `mbrola_voice_unavailable` | `de6` voice missing | `sudo apt install mbrola-de6` |
| Audio returns `unknown_card` | Card ID not in practice content | Refresh the queue and verify content import |
| Practice panel shows "Could not reach MiraLingo auth" | Backend not running | Start with `./scripts/start_miralingo.sh` |
| Login fails with `local_admin_disabled` | Not in development mode | Set `MIRALINGO_ENV=development` |
| `401 unauthenticated` on practice endpoints | No session cookie | Login first via `/auth/login` |
| Empty practice queue | No cards imported | Verify `data/phrases/english-mirad-sentence-pairs.csv` exists |

All error responses are structured JSON without stack traces or credential echoes.

---

## Database Inspection

Safe SQLite queries for local diagnostics:

```bash
python3 - <<'PY'
import sqlite3
db = sqlite3.connect('.miralingo/miralingo.sqlite3')
for table in ('users', 'shown_cards', 'answer_events', 'practice_sessions', 'practice_lifecycle'):
    count = db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'{table}: {count} rows')
db.close()
PY
```

**Caution:** Never print or log the `salt` or `password_hash` columns from the `users` table.

---

## License

MIT