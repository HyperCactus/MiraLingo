# M004 Scope and Boundary Map

This document is the tracked, executable scope contract for the M004 MiraLingo web app milestone. It exists outside `.gsd/` so repository tests and future validators can inspect the milestone boundary without scraping planning internals.

## Canonical Boundary Map Artifact

This tracked document is the canonical validation-linked producer and consumer boundary map for M004. It intentionally serves as the auditable boundary-map source of truth while the roadmap-level `Boundary Map` placeholder remains non-substantive; validators and tests should link here instead of reading `.gsd/` planning files or inventing requirement IDs.

The map covers S01-S11 and traces each cross-slice webapp contract from producer slice, to concrete provided contract, to consumer or validation use, to evidence and diagnostic surfaces. It is documentation-only: no runtime source, API behavior, persistence schema, scheduler logic, audio behavior, or frontend behavior is changed by this artifact.

## Requirement Status

The project requirements database currently has no Active requirements. It contains only validated non-webapp tokenizer requirements:

| Requirement | Current status | M004 impact |
|---|---|---|
| R001 | Validated tokenizer behavior for ordinary Mirad text | Foundation only; no M004 webapp ownership. |
| R009 | Validated tokenizer rejection of legacy accented orthography | Foundation only; no M004 webapp ownership. |

Because there are zero Active DB requirements, M004 does not invent new requirement identifiers. M004 validation maps the milestone acceptance criteria and roadmap promises listed in the milestone context to completed S01-S11 evidence or explicit out-of-scope items.

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
| S10 | Requirement scope reconciliation | Produce validation-ready R001/R009 scope reconciliation, zero Active requirement wording, non-synthetic requirement guidance, and pytest guards over the tracked document. | Completed evidence for R001/R009 foundation scope, zero Active DB requirements, and completed S07-S09 evidence mapped without `.gsd/` scraping. | S11 boundary restoration and M004 validation consume S10 to preserve requirement scope truth. |
| S11 | Boundary map restoration | Produce this explicit canonical boundary-map section, S01-S11 coverage, and cross-slice producer/consumer traceability for major M004 contract surfaces. | Completed by this tracked artifact when repository checks confirm it is non-empty, placeholder-free, and traceable without `.gsd/` files. | M004 validation consumes S11 as the durable replacement for the missing roadmap boundary-map content. |

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

The following table is the cross-slice producer/consumer trace map for M004 validation. Each row names the major contract surface, the producing slice or slices, the concrete provided contract, the consumer slice or validation use, the tracked evidence source, and the diagnostic or inspection surface available when behavior is unavailable or needs validation.

| Contract surface | Producer slice(s) | Concrete provided contract | Consumer slice(s) or validation use | Evidence source | Diagnostic or inspection surface |
|---|---|---|---|---|---|
| Auth/session | S01, extended by S07 and persisted by S08 | FastAPI session endpoints for current user, login, logout, signed-cookie auth state, guarded development-only `admin`, password-free user payloads, and authenticated app shell behavior. | S03 practice APIs, S04 audio, S05 integrated flow, S07 registration/logout, S08 SQLite users, S09 browser UAT, and M004 validation. | S01 auth/welcome evidence, S07 registration/logout tests, S08 SQLite user persistence evidence, S09 browser walkthrough. | `/auth/current-user`, `/auth/login`, `/auth/logout`, browser auth UI, HTTP status codes, structured JSON errors, and SQLite `users` rows without password echoing. |
| Registration | S07, persisted by S08 | Learner account creation, registered login/current-user/logout flow, authenticated access control, and failure-state coverage for duplicate or invalid credentials. | S08 persistence, S09 final UAT, and validation of non-admin learner entry. | S07 completed evidence and S08 durable user storage evidence. | Registration UI state, auth endpoint responses, credential-redacted errors, and SQLite `users` table inspection under explicit test database paths. |
| Content importer | S02, strengthened by S08 | Deterministic phrase cards from CSV, exclusion of one-word English phrase rows, wordfreq-ranked word candidates accepted through Mirad lexicon lookup, import counts, duplicate handling, and lexicon miss diagnostics. | S03 scheduler, S04 audio text resolution, S05 integrated practice, S07 bidirectional practice, S08 persistence, S09 browser UAT, and validation. | S02 importer evidence and S08 wordfreq plus lexicon lookup evidence. | Import preview/command output, imported/skipped/missed counts, lexicon miss diagnostics, stable card IDs, and card rows persisted to SQLite. |
| Practice scheduler and answer events | S03, extended by S07 and persisted by S08 | Authenticated practice queue, stable card IDs, answer submission, normalized answer checking in English to Mirad and Mirad to English directions, scheduler reasons, weak-item prioritization, stale mastered review, new-item gating, bounded session history, and correctness events. | Frontend practice UI, S05 integrated flow, S07 direction tests, S08 durable event storage, S09 UAT, progress diagnostics, and validation. | S03 scheduler evidence, S07 bidirectional word/phrase practice evidence, S08 shown-card and answer-event persistence evidence, S09 UAT. | Practice queue/answer API responses, scheduler reason fields, per-card event data, SQLite `shown_cards` and `answer_events`, and progress summaries. |
| Audio service | S04 | Card-bound MBROLA audio endpoint that returns deterministic WAV success headers when host audio dependencies are available or structured unavailable diagnostics when MBROLA or voice assets are absent. | Frontend speaker controls, S05 integrated flow, S09 browser UAT, and validation of success-or-diagnostic audio acceptance. | S04 audio API/control evidence, S05 integrated audio flow, S09 browser audio fallback or success evidence. | Audio endpoint status, WAV content headers on success, structured unavailable JSON on host-dependent failure, frontend unavailable state, and no client-selected output paths. |
| Progress diagnostics | S05, fed by S03/S07/S08 | `/practice/progress` totals, per-type and per-card summaries, latest event, weak/mastered/stale/new counts, UI progress panel, and credential-redacted diagnostic responses. | Frontend progress panel, S05 UAT, S09 browser UAT, and milestone validation. | S05 progress evidence, S08 persisted event/progress evidence, S09 final browser progress evidence. | `/practice/progress` response, progress UI, scheduler event model, SQLite answer history, and stacktrace-free structured failure states. |
| SQLite persistence | S08 | Durable SQLite-backed users, cards, practice sessions, shown-card rows, answer events, mastery state, and audio metadata across app/client instances. | Auth/session, registration, scheduler, progress, browser UAT, and validation of persistence acceptance criteria. | S08 integration evidence and S09 SQLite persistence inspection. | Explicit test database paths, SQLite `users`, `cards`, `shown_cards`, and `answer_events` tables, plus isolated state setup in tests. |
| Frontend UAT | S09, consuming S01-S08 | Live browser flow for welcome, registration or login, mixed word/phrase practice, audio success or unavailable diagnostics, progress stats, logout, full webapp pytest, and frontend production build. | M004 final user-visible acceptance and validation closeout. | S09 deterministic UAT tests, live browser walkthrough, full webapp regression, and frontend build evidence. | Browser-visible welcome/auth/practice/audio/progress/logout UI, explicit UAT assertions, build output, and structured backend diagnostics surfaced in the UI. |
| Requirement-scope reconciliation | S10, preserved by S11 | Zero Active DB requirements, R001/R009 classified as already-validated tokenizer foundation outside M004 webapp ownership, no synthetic requirement IDs, and validation mapped to milestone acceptance criteria. | S11 boundary map restoration and M004 validation. | S10 completed evidence and this S11 canonical boundary-map artifact. | Diagnostic repository pytest contract over `packages/webapp/docs/m004_scope_boundary_map.md`, explicit text checks for R001/R009 scope, and no `.gsd/` scraping. |

## Remediation Ownership

| Gap | Owner slice | Required proof before M004 completion | Status |
|---|---|---|---|
| Registration beyond local development admin | S07 | User can create an account, log in, log out, and tests cover both successful and failure states. | Completed by S07. |
| Bidirectional word and phrase practice | S07 | Tests prove English to Mirad and Mirad to English directions for word and phrase cards, including answer checking and UI labels. | Completed by S07. |
| Real wordfreq source integration | S08 | Import tests prove word cards come from wordfreq-ranked candidates and lexicon lookup, with counts for hits and misses. | Completed by S08. |
| SQLite card, session, review, and mastery persistence | S08 | Integration tests prove shown cards and correctness events are durable across new app/client instances. | Completed by S08. |
| Final live browser UAT | S09 | Browser evidence covers welcome, registration or login, mixed practice, audio success or unavailable diagnostics, and progress stats. | Completed by S09. |
| Requirement scope reconciliation | S10 | R001/R009 are explicitly scoped as validated tokenizer foundation requirements outside M004 webapp ownership, zero Active requirements are named, and no synthetic requirement IDs are introduced. | Completed by S10. |
| Canonical producer/consumer boundary map | S11 | This tracked document states it is the validation-linked boundary artifact, includes S01-S11 traceability, and maps cross-slice contracts without reading `.gsd/` files. | Completed by S11 through this artifact. |

## Validation Evidence

| Evidence source | Covers | Limitations |
|---|---|---|
| S01 completed evidence | Welcome page, local admin login, guarded development auth shell. | Does not by itself prove later registration or persistence work. |
| S02 completed evidence | Deterministic phrase import and word import contract with diagnostics. | Later S08 evidence supplies real wordfreq sourcing and SQLite persistence. |
| S03 completed evidence | Practice queue, answer submission, scheduler priorities, and session events. | Later S07 and S08 evidence supply reverse prompt directions and durable storage. |
| S04 completed evidence | Card-bound MBROLA audio API and structured unavailable diagnostics. | Actual audible playback depends on host MBROLA and `de6` availability; validation accepts either deterministic WAV success or structured unavailable diagnostics. |
| S05 completed evidence | Integrated logged-out to admin login to mixed practice to audio to progress flow, plus progress API/UI. | S09 reruns final browser evidence after registration and persistence remediation. |
| S06 completed evidence | Auditable scope, producer/consumer boundary, validation ownership, and placeholder-free validation contract. | It is a planning diagnostic, not runtime proof by itself. |
| S07 completed evidence | Learner registration, current-user, logout, authenticated access control, and bidirectional word/phrase practice in English to Mirad and Mirad to English. | Learner accounts remain process-local until the S08 SQLite migration. |
| S08 completed evidence | wordfreq-ranked word cards, lexicon lookup acceptance, SQLite-backed learner accounts, shown-card rows, answer-event rows, progress, and scheduler persistence across app restarts. | No live browser walkthrough was performed until S09. |
| S09 completed evidence | Final deterministic UAT regressions, live browser walkthrough for welcome/auth/practice/audio/progress/logout, SQLite persistence checks, full webapp pytest, and frontend production build. | Local audible playback was not proven in automation; safe audio fallback plus deterministic WAV/unavailable diagnostic tests cover acceptance. |
| S10 completed evidence | Requirement-scope reconciliation for zero Active DB requirements, R001/R009 tokenizer foundation scope, non-synthetic requirement IDs, and completed S07-S09 evidence. | It does not replace the producer/consumer boundary map by itself; S11 restores that canonical map here. |
| S11 completed evidence | Canonical validation-linked boundary-map wording, S01-S11 slice traceability, and cross-slice contract traceability for auth/session, registration, importer, scheduler/events, audio, progress, SQLite, frontend UAT, and requirement reconciliation. | Documentation-only validation surface; it intentionally changes no runtime behavior. |

## Validation Rules for Future Executors

- Use this tracked document as the canonical M004 boundary-map artifact when roadmap-level boundary wording is absent or only points to a placeholder.
- When validating requirements, report that the DB requirements file has zero Active requirements and two validated non-webapp tokenizer requirements: R001 and R009.
- Treat R001 and R009 as already-validated foundation behavior outside M004 webapp ownership; do not count them as M004-delivered requirements and do not revalidate them as webapp slices.
- Validate M004 through the milestone acceptance criteria and completed S01-S11 evidence in this document instead of creating synthetic requirement IDs.
- Use S07 evidence for final registration, logout, and bidirectional word/phrase practice acceptance.
- Use S08 evidence for final word-card source and persistence acceptance: wordfreq-ranked candidates, lexicon lookup, SQLite-backed users, shown cards, answer events, and progress state.
- Use S09 evidence for final user-visible acceptance: live browser UAT after S07 and S08, plus full regression and frontend build evidence.
- Use S10 evidence for final requirement-scope reconciliation: zero Active requirements, R001/R009 tokenizer foundation scope, and no synthetic requirement IDs.
- Use S11 evidence for final cross-slice producer/consumer traceability and as the validation-linked replacement for the missing roadmap boundary-map content.
- Preserve credential redaction and structured diagnostics when adding future auth, storage, practice, audio, or progress behavior.
