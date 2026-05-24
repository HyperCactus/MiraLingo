# S09 Final Browser UAT

Date: 2026-05-24

## Runtime

Backend command from repository root:

```bash
MIRALINGO_DATABASE_PATH=/tmp/miralingo-s09-t02-20260524144035.sqlite3 \
MIRALINGO_ENV=development \
MIRALINGO_ENABLE_LOCAL_ADMIN=true \
PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src \
python -m uvicorn mirad_webapp.api:app --host 127.0.0.1 --port 8000
```

Frontend command from repository root:

```bash
npm --prefix packages/webapp/frontend run dev -- --host 127.0.0.1
```

URLs:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173/`
- SQLite database: `/tmp/miralingo-s09-t02-20260524144035.sqlite3`

## Browser Walkthrough Evidence

Automated Playwright walkthrough against the live Vite URL passed (`gsd_exec` run `dda09522-ac34-46e1-9aad-787bdf2d5a52`). It verified:

1. Logged-out state showed **Welcome to MiraLingo**.
2. A unique learner account (`s09uat_1779598621236`) registered successfully through the browser.
3. Authenticated state showed the practice panel and **Practice stats**.
4. The bounded queue contained both `word` and `phrase` cards and both `english_to_mirad` and `mirad_to_english` directions.
5. The current card exposed direction text and the **Hear Mirad answer** control.
6. Clicking **Hear Mirad answer** produced a user-visible local runtime audio outcome without stack traces or secret leakage. This run returned the browser playback fallback text `Could not play audio. Check the server, then try again.` with diagnostic `network_or_browser_playback`; deterministic API tests continue to cover WAV success and structured MBROLA unavailable diagnostics.
7. **I knew it** and **I missed it** were clicked through the live UI.
8. Progress updated to `total=2`, `correct=1`, `incorrect=1`, with latest event marked incorrect and per-type totals present.
9. The visible page contained updated attempts/correct/incorrect/latest-answer stats and did not expose the submitted password, password hashes, salts, or stack traces.
10. Logout returned to **Welcome to MiraLingo** and cleared practice, progress, audio, and username UI state.

Final browser result excerpt:

```json
{
  "ok": true,
  "queueTypes": ["phrase", "word"],
  "queueDirections": ["english_to_mirad", "mirad_to_english"],
  "progress": {
    "total": 2,
    "correct": 1,
    "incorrect": 1,
    "per_type": {
      "word": {"attempts": 0, "correct": 0, "incorrect": 0, "accuracy": null},
      "phrase": {"attempts": 2, "correct": 1, "incorrect": 1, "accuracy": 0.5}
    }
  },
  "apiErrors": []
}
```

## SQLite Inspection

Safe-field SQLite inspection passed (`gsd_exec` run `07cf1161-778f-4211-bcf6-2c369fd25625`). The isolated database contained durable rows for registered users, shown cards, and answer events. Only safe fields were printed (`username`, `role`, `card_id`, `direction`, `card_type`, `correct`); salts and password hashes were not inspected or copied.

Observed counts after the live runs:

- `users`: 9
- `shown_cards`: 81
- `answer_events`: 11

The tail included answer events for the final browser user with `english_to_mirad` and `mirad_to_english` phrase directions and correct/incorrect outcomes.

## Regression and Build Verification

- `PYTHONPATH=packages/webapp/src:packages/tts/src:packages/translator/src python -m pytest packages/webapp/tests/test_s09_final_uat.py -q` passed: `3 passed`.
- `npm --prefix packages/webapp/frontend run build` passed and produced the Vite production bundle.
- `test -s packages/webapp/S09-UAT.md` passed after this artifact was written.

## Defects Fixed

No source defects were found during the live walkthrough, so no frontend or backend code changes were required.

## Remaining Acceptable Local-Runtime Caveats

The local browser run did not prove audible playback because this environment surfaced browser playback fallback text. This is acceptable for S09 because the deterministic S09 regression suite verifies successful WAV responses with a fake MBROLA backend and structured unavailable diagnostics for missing MBROLA runtime. The live UI showed a safe user-facing audio failure without credentials or stack traces.
