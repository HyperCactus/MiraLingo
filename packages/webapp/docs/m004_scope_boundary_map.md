# M004 Scope and Boundary Map

This document is the tracked, executable scope contract for the M004 MiraLingo web app milestone. It exists outside `.gsd/` so repository tests and future validators can inspect the milestone boundary without scraping planning internals.

## Requirement Status

The project requirements database currently has no Active requirements. It contains only validated non-webapp tokenizer requirements:

| Requirement | Current status | M004 impact |
|---|---|---|
| R001 | Validated tokenizer behavior for ordinary Mirad text | Foundation only; no M004 webapp ownership. |
| R009 | Validated tokenizer rejection of legacy accented orthography | Foundation only; no M004 webapp ownership. |

Because there are zero Active DB requirements, M004 does not invent new requirement identifiers. M004 validation maps the milestone acceptance criteria and roadmap promises listed in the milestone context to completed S01-S09 evidence or explicit out-of-scope items.

## Requirement Scope Reconciliation

The canonical requirements source, `.gsd/REQUIREMENTS.md`, reports zero Active requirements and two Validated requirements. Both validated requirements are tokenizer foundation requirements that predate and support the broader product, not M004 webapp acceptance items.

- R001 is already validated tokenizer behavior for ordinary Mirad text: tokenizing `At tixe Mirad.` preserves ordinary words, spaces, numbers, and punctuation. M004 may rely on this tokenizer foundation, but no M004 webapp slice owns or revalidates R001.
- R009 is already validated tokenizer rejection of legacy accented orthography: tokenizing legacy accented input such as `café` raises `UnsupportedLegacyOrthographyError`. M004 may rely on that foundation behavior where text processing is reused, but no M004 webapp slice owns or revalidates R009.
- Neither R001 nor R009 should be counted as M004-delivered webapp functionality, and neither should be used to create synthetic M004 requirement IDs.
- M004 validation should cover the milestone acceptance criteria from `M004-CONTEXT.md`: welcome/auth, registration/logout, mixed word and phrase practice in both directions, deterministic content import, wordfreq plus lexicon-backed word cards, MBROLA audio success or diagnostics, SQLite persistence, adaptive scheduling, progress stats, and final browser UAT evidence.

## Requirement Coverage by Slice

| Slice | Scope promise | Producer responsibilities | Current status | Consumer or validation use |
|---|---|---|---|---|
| S01 | Local auth and welcome shell | Produce FastAPI auth endpoints, signed-cookie session state, development-only `admin` login, logged-out welcome UI, and authenticated app shell. | Completed evidence for welcome page, guarded local admin login, auth state, and app shell. | S05 integrated flow, S07 registration/logout, and S09 browser UAT consume auth and welcome behavior. |
| S02 | Content import | Produce deterministic phrase and word card import contracts, phrase filtering for two-or-more-word English rows, import counts, and source diagnostics. | Completed evidence for deterministic importer contract and content diagnostics. | S03, S05, S07, S08, and S09 consume imported phrase/word card boundaries. |
| S03 | Queue, events, and scheduler | Produce authenticated practice queue, answer submission, bounded session event history, answer normalization, weak item prioritization, stale review, and new-item gating. | Completed evidence for practice queue, answer recording, scheduler priorities, progress inputs, and session event behavior. | S05 integrated flow, S07 bidirectional practice, S08 persistence, and S09 final UAT consume scheduler and event contracts. |
| S04 | Audio | Produce card-bound MBROLA audio endpoint, WAV success headers, structured unavailable diagnostics, and frontend speaker controls. | Completed evidence for audio API, frontend controls, deterministic WAV or structured unavailable behavior, and host-dependent diagnostics. | S05 integrated flow and S09 final UAT consume audio success-or-diagnostic behavior. |
| S05 | Integrated progress flow | Produce logged-out welcome to admin login to mixed practice to audio to progress flow, `/practice/progress`, UI progress panel, and runtime UAT runbook. | Completed evidence for integrated logged-out, admin login, mixed practice, audio, and progress flow. | S06 boundary mapping and S09 final UAT consume S05 as integrated baseline evidence. |
| S06 | Boundary and validation artifacts | Produce this tracked scope document, executable pytest contract, roadmap boundary map basis, and validation gap explanation. | Completed evidence for scope boundaries, producer/consumer contracts, and validation ownership diagnostics. | S07-S09 used S06 ownership to close remediation gaps; M004 validation consumes the refreshed reconciliation here. |
| S07 | Registration and bidirectional practice | Produce registration, login, logout, and practice tests for English to Mirad and Mirad to English directions across word and phrase cards. | Completed evidence for learner registration, registered login/current-user/logout, authenticated access control, and bidirectional word/phrase practice. | S08 persistence and S09 final UAT consume registration, logout, and direction-aware practice contracts. |
| S08 | Wordfreq source and SQLite persistence | Produce real wordfreq-ranked word source integration, lexicon lookup acceptance, SQLite-backed card/session/review persistence, and integration tests proving shown-card events survive process/session boundaries. | Completed evidence for wordfreq-ranked word cards, lexicon lookup diagnostics, SQLite learner persistence, shown-card history, and answer-event history across app restarts. | S09 final UAT and milestone validation consume durable storage and real word-source evidence. |
| S09 | Browser UAT | Produce live browser walkthrough evidence for welcome, registration or login, mixed practice, audio success or unavailable diagnostics, and progress stats. | Completed evidence for final deterministic UAT tests, live browser walkthrough, SQLite persistence inspection, full webapp pytest, and frontend production build. | M004 milestone validation consumes S09 as final user-visible acceptance evidence. |

## Scope Boundaries

### In Scope for M004

- FastAPI backend APIs for health, auth, content import preview, practice queue, answer submission, audio, and progress diagnostics.
- Svelte frontend surfaces for welcome, authentication actions, practice, audio affordances, progress, and local UAT checks.
- Deterministic phrase cards from `data/phrases/english-mirad-sentence-pairs.csv`, with one-word English rows excluded.
- Word cards sourced from wordfreq-ranked candidates and accepted only when Mirad lexicon lookup succeeds.
- MBROLA-backed Mirad audio through `packages/tts`, with structured unavailable diagnostics when the host runtime lacks MBROLA or the `de6` voice.
- Adaptive scheduling based on correctness, mastery, recency, stale mastered review, and new-item gating.
- SQLite persistence for users, cards, practice sessions, review events, mastery state, and audio metadata.
- Local Docker or development startup documentation sufficient for final UAT.

### Out of Scope for M004

- Completing remaining M003 translator optimization, arbitrary live translation, or round-trip evaluation.
- Cloud services for the core learning loop.
- Production hardening beyond explicit prevention of default admin credentials outside development mode.
- Social auth, email verification, password-reset email delivery, or an admin dashboard.
- Mobile app or PWA packaging.
- Generating a full future corpus before the smaller learner loop works.

## Producer and Consumer Contracts

| Producer | Provides | Consumers | Boundary rule |
|---|---|---|---|
| Auth API and session middleware | `/auth/current-user`, `/auth/login`, `/auth/logout`, password-free user payloads, and guarded local admin behavior. | Frontend shell, practice APIs, audio endpoint, progress endpoint, S05 flow, S07 registration/logout, S09 browser UAT. | Auth failures must return structured JSON without credential echoing; local `admin` credentials are development-only. |
| Registration flow | User creation flow, login/logout coverage, and tests proving non-admin account entry. | Frontend auth UI, persistence storage, browser UAT, milestone validation. | Registration creates learner accounts without exposing password material; durable storage is supplied by the S08 SQLite boundary. |
| Content importer | Phrase and word cards, import counts, duplicate handling, one-word phrase filtering, lexicon miss diagnostics. | Practice queue, scheduler, audio resolver, progress, SQLite persistence, final UAT. | Importers expose counts and stable card records; callers do not pass arbitrary filesystem paths through public practice APIs. |
| Practice scheduler | Bounded queue, stable card ids, answer events, scheduler reasons, mastery and recency diagnostics. | Frontend practice UI, progress aggregation, S05 integrated flow, S07 direction tests, S08 persistence, S09 browser UAT. | Scheduler ranks normalized cards/events; persistence preserves the same event fields rather than inventing a divergent event shape. |
| Audio service | Card-bound MBROLA WAV responses or structured unavailable diagnostics. | Frontend speaker control, S05 flow, S09 browser UAT. | Audio accepts stable card ids only, resolves Mirad text server-side, and does not accept client-selected output paths. |
| Progress diagnostics | `/practice/progress` totals, per-type/per-card summaries, latest event, weak/mastered/stale/new counts. | Frontend progress panel, S05 UAT, S09 browser UAT. | Progress uses the scheduler event model and must stay credential-redacted and stacktrace-free. |
| SQLite persistence | Durable users, cards, sessions, review events, mastery state, and audio metadata. | Practice scheduler, progress API, browser UAT, milestone validation. | SQLite state is inspectable through `users`, `shown_cards`, and `answer_events`; tests isolate state with explicit database paths. |
| Frontend Svelte app | User-visible welcome, registration/login/logout, practice, audio, and progress surfaces. | Manual and automated browser UAT. | UI must reflect backend structured states rather than hiding unavailable audio, auth failures, or progress errors. |

## Remediation Ownership

| Gap | Owner slice | Required proof before M004 completion | Status |
|---|---|---|---|
| Registration beyond local development admin | S07 | User can create an account, log in, log out, and tests cover both successful and failure states. | Completed by S07. |
| Bidirectional word and phrase practice | S07 | Tests prove English to Mirad and Mirad to English directions for word and phrase cards, including answer checking and UI labels. | Completed by S07. |
| Real wordfreq source integration | S08 | Import tests prove word cards come from wordfreq-ranked candidates and lexicon lookup, with counts for hits and misses. | Completed by S08. |
| SQLite card, session, review, and mastery persistence | S08 | Integration tests prove shown cards and correctness events are durable across new app/client instances. | Completed by S08. |
| Final live browser UAT | S09 | Browser evidence covers welcome, registration or login, mixed practice, audio success or unavailable diagnostics, and progress stats. | Completed by S09. |

## Validation Evidence

| Evidence source | Covers | Limitations |
|---|---|---|
| S01 completed evidence | Welcome page, local admin login, guarded development auth shell. | Does not by itself prove later registration or persistence work. |
| S02 completed evidence | Deterministic phrase import and word import contract with diagnostics. | Later S08 evidence supplies real wordfreq sourcing and SQLite persistence. |
| S03 completed evidence | Practice queue, answer submission, scheduler priorities, and session events. | Later S07 and S08 evidence supply reverse prompt directions and durable storage. |
| S04 completed evidence | Card-bound MBROLA audio API and structured unavailable diagnostics. | Actual audible playback depends on host MBROLA and `de6` availability. |
| S05 completed evidence | Integrated logged-out to admin login to mixed practice to audio to progress flow, plus progress API/UI. | S09 reruns final browser evidence after registration and persistence remediation. |
| S06 completed evidence | Auditable scope, producer/consumer boundary, validation ownership, and placeholder-free validation contract. | It is a planning diagnostic, not runtime proof by itself. |
| S07 completed evidence | Learner registration, current-user, logout, authenticated access control, and bidirectional word/phrase practice in English to Mirad and Mirad to English. | Learner accounts remain process-local until the S08 SQLite migration. |
| S08 completed evidence | wordfreq-ranked word cards, lexicon lookup acceptance, SQLite-backed learner accounts, shown-card rows, answer-event rows, progress, and scheduler persistence across app restarts. | No live browser walkthrough was performed until S09. |
| S09 completed evidence | Final deterministic UAT regressions, live browser walkthrough for welcome/auth/practice/audio/progress/logout, SQLite persistence checks, full webapp pytest, and frontend production build. | Local audible playback was not proven in automation; safe audio fallback plus deterministic WAV/unavailable diagnostic tests cover acceptance. |

## Validation Rules for Future Executors

- When validating requirements, report that the DB requirements file has zero Active requirements and two validated non-webapp tokenizer requirements: R001 and R009.
- Treat R001 and R009 as already-validated foundation behavior outside M004 webapp ownership; do not count them as M004-delivered requirements and do not revalidate them as webapp slices.
- Validate M004 through the milestone acceptance criteria and completed S01-S09 evidence in this document instead of creating synthetic requirement IDs.
- Use S07 evidence for final registration, logout, and bidirectional word/phrase practice acceptance.
- Use S08 evidence for final word-card source and persistence acceptance: wordfreq-ranked candidates, lexicon lookup, SQLite-backed users, shown cards, answer events, and progress state.
- Use S09 evidence for final user-visible acceptance: live browser UAT after S07 and S08, plus full regression and frontend build evidence.
- Preserve credential redaction and structured diagnostics when adding future auth, storage, practice, audio, or progress behavior.
