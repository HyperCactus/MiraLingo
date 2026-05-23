# M004 Scope and Boundary Map

This document is the tracked, executable scope contract for the M004 MiraLingo web app milestone. It exists outside `.gsd/` so repository tests and future validators can inspect the milestone boundary without scraping planning internals.

## Requirement Status

The project requirements database currently has no Active requirements. It contains only validated non-webapp tokenizer requirements:

| Requirement | Current status | M004 impact |
|---|---|---|
| R001 | Validated tokenizer behavior for ordinary Mirad text | Foundation only; no M004 webapp ownership. |
| R009 | Validated tokenizer rejection of legacy accented orthography | Foundation only; no M004 webapp ownership. |

Because there are zero Active DB requirements, S06 does not invent new requirement identifiers. M004 validation must instead map the milestone acceptance criteria and roadmap promises listed in the milestone context to completed evidence, pending remediation slices, or explicit out-of-scope items.

## Requirement Coverage by Slice

| Slice | Scope promise | Producer responsibilities | Current status | Consumer or validation use |
|---|---|---|---|---|
| S01 | Local auth and welcome shell | Produce FastAPI auth endpoints, signed-cookie session state, development-only `admin` login, logged-out welcome UI, and authenticated app shell. | Covered by completed slice evidence. | S05 integrated flow consumes auth state; S07 must extend this surface with registration and logout coverage. |
| S02 | Content import | Produce deterministic phrase and word card import contracts, phrase filtering for two-or-more-word English rows, import counts, and source diagnostics. | Covered for deterministic importer contract. | S03 and S05 consume imported cards; S08 must replace fallback word candidates with a real wordfreq-ranked source plus SQLite persistence. |
| S03 | Queue, events, and scheduler | Produce authenticated practice queue, answer submission, bounded session event history, answer normalization, weak item prioritization, stale review, and new-item gating. | Covered for session-scoped behavior. | S05 consumes queue and event contracts; S07 must prove both prompt directions; S08 must persist shown-card events beyond session memory. |
| S04 | Audio | Produce card-bound MBROLA audio endpoint, WAV success headers, structured unavailable diagnostics, and frontend speaker controls. | Covered with deterministic tests and host-dependent runtime diagnostics. | S05 consumes audio in integrated flow; S09 must verify audio success or clear unavailable diagnostics in a live browser walkthrough. |
| S05 | Integrated progress flow | Produce logged-out welcome to admin login to mixed practice to audio to progress flow, `/practice/progress`, UI progress panel, and final runtime UAT runbook. | Covered by completed slice evidence. | S06 uses S05 evidence as the latest integrated proof; S09 must rerun the flow in a live browser after remaining remediations. |
| S06 | Boundary and validation artifacts | Produce this tracked scope document, executable pytest contract, roadmap boundary map basis, and validation gap explanation. | In progress in this task. | M004 validation consumes this document to explain what is covered, pending, and scoped out. |
| S07 | Registration and bidirectional practice | Produce registration, login, logout, and practice tests for English to Mirad and Mirad to English directions across word and phrase cards. | Pending remediation owned by S07. | S09 and milestone validation consume these proofs before claiming final acceptance for registration and bidirectional practice. |
| S08 | Wordfreq source and SQLite persistence | Produce real wordfreq-ranked word source integration, lexicon lookup acceptance, SQLite-backed card/session/review persistence, and integration tests proving shown-card events survive process/session boundaries. | Pending remediation owned by S08. | Scheduler, progress, and final UAT consume durable storage before final milestone completion. |
| S09 | Browser UAT | Produce live browser walkthrough evidence for welcome, registration or login, mixed practice, audio success or unavailable diagnostics, and progress stats. | Pending remediation owned by S09. | M004 milestone validation consumes S09 as final user-visible acceptance evidence. |

## Scope Boundaries

### In Scope for M004

- FastAPI backend APIs for health, auth, content import preview, practice queue, answer submission, audio, and progress diagnostics.
- Svelte frontend surfaces for welcome, authentication actions, practice, audio affordances, progress, and local UAT checks.
- Deterministic phrase cards from `data/phrases/english-mirad-sentence-pairs.csv`, with one-word English rows excluded.
- Word cards sourced from wordfreq-ranked candidates and accepted only when Mirad lexicon lookup succeeds.
- MBROLA-backed Mirad audio through `packages/tts`, with structured unavailable diagnostics when the host runtime lacks MBROLA or the `de6` voice.
- Adaptive scheduling based on correctness, mastery, recency, stale mastered review, and new-item gating.
- SQLite persistence for users, cards, practice sessions, review events, mastery state, and audio metadata after S08 completes.
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
| Auth API and session middleware | `/auth/current-user`, `/auth/login`, `/auth/logout`, password-free user payloads, and guarded local admin behavior. | Frontend shell, practice APIs, audio endpoint, progress endpoint, S05 flow, S07 registration remediation. | Auth failures must return structured JSON without credential echoing; local `admin` credentials are development-only. |
| Registration remediation | User creation flow, login/logout coverage, and tests proving non-admin account entry. | Frontend auth UI, browser UAT, milestone validation. | S07 owns this gap; earlier slices must not claim final registration acceptance. |
| Content importer | Phrase and word cards, import counts, duplicate handling, one-word phrase filtering, lexicon miss diagnostics. | Practice queue, scheduler, audio resolver, progress, S08 persistence. | Importers expose counts and stable card records; callers do not pass arbitrary filesystem paths through public practice APIs. |
| Practice scheduler | Bounded queue, stable card ids, answer events, scheduler reasons, mastery and recency diagnostics. | Frontend practice UI, progress aggregation, S05 integrated flow, S07 direction tests, S08 persistence. | Scheduler ranks normalized cards/events; persistence layer must preserve the same event fields rather than inventing a divergent event shape. |
| Audio service | Card-bound MBROLA WAV responses or structured unavailable diagnostics. | Frontend speaker control, S05 flow, S09 browser UAT. | Audio accepts stable card ids only, resolves Mirad text server-side, and does not accept client-selected output paths. |
| Progress diagnostics | `/practice/progress` totals, per-type/per-card summaries, latest event, weak/mastered/stale/new counts. | Frontend progress panel, S05 UAT, S09 browser UAT. | Progress uses the scheduler event model and must stay credential-redacted and stacktrace-free. |
| SQLite persistence remediation | Durable users, cards, sessions, review events, mastery state, and audio metadata. | Practice scheduler, progress API, browser UAT, milestone validation. | S08 owns durable storage; session-only evidence remains insufficient for final persistence acceptance. |
| Frontend Svelte app | User-visible welcome, auth, practice, audio, and progress surfaces. | Manual and automated browser UAT. | UI must reflect backend structured states rather than hiding unavailable audio, auth failures, or progress errors. |

## Remediation Ownership

| Gap | Owner slice | Required proof before M004 completion | Status |
|---|---|---|---|
| Registration beyond local development admin | S07 | User can create an account, log in, log out, and tests cover both successful and failure states. | Pending remediation. |
| Bidirectional word and phrase practice | S07 | Tests prove English to Mirad and Mirad to English directions for word and phrase cards, including answer checking and UI labels. | Pending remediation. |
| Real wordfreq source integration | S08 | Import tests prove word cards come from wordfreq-ranked candidates and lexicon lookup, with counts for hits and misses. | Pending remediation. |
| SQLite card, session, review, and mastery persistence | S08 | Integration tests prove shown cards and correctness events are durable across new app/client instances. | Pending remediation. |
| Final live browser UAT | S09 | Browser evidence covers welcome, registration or login, mixed practice, audio success or unavailable diagnostics, and progress stats. | Pending remediation. |

## Validation Evidence

| Evidence source | Covers | Limitations |
|---|---|---|
| S01 completed evidence | Welcome page, local admin login, guarded development auth shell. | Does not prove registration. |
| S02 completed evidence | Deterministic phrase import and word import contract with diagnostics. | Final wordfreq source and SQLite persistence remain S08-owned. |
| S03 completed evidence | Practice queue, answer submission, scheduler priorities, and session events. | Does not prove reverse prompt direction or durable storage. |
| S04 completed evidence | Card-bound MBROLA audio API and structured unavailable diagnostics. | Actual audible playback depends on host MBROLA and `de6` availability. |
| S05 completed evidence | Integrated logged-out to admin login to mixed practice to audio to progress flow, plus progress API/UI. | Browser click-through must be rerun after S07 and S08 by S09. |
| This S06 document and pytest contract | Auditable scope, producer/consumer boundary, remediation ownership, and placeholder-free validation contract. | It is a planning diagnostic, not runtime proof of pending S07-S09 behavior. |

## Validation Rules for Future Executors

- Do not claim final M004 registration acceptance until S07 evidence exists.
- Do not claim final bidirectional practice acceptance until S07 proves both English to Mirad and Mirad to English for words and phrases.
- Do not claim final word-card source acceptance until S08 proves real wordfreq-ranked candidates and lexicon lookup.
- Do not claim final persistence acceptance until S08 proves SQLite-backed users, sessions, shown cards, review events, and mastery state.
- Do not claim final user-visible acceptance until S09 records a live browser UAT after S07 and S08 complete.
- When validating requirements, report that the DB requirements file has zero Active requirements and two validated non-webapp tokenizer requirements, then map M004 acceptance criteria through this document instead of creating synthetic requirement IDs.
