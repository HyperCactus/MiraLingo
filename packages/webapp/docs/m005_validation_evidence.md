# M005 Validation Evidence Index

This document is the tracked validation index for the M005 MiraLingo learner-flow milestone. It exists in `packages/webapp/docs/` so milestone validation can cite repository-tracked proof without scraping `.gsd/` planning files or rewriting completed slice summaries.

It is documentation-only. It does not add product behavior, revise prior slice claims, or claim proof that only exists in local agent state. When live browser, audible playback, or external Iconify behavior cannot be made fully deterministic in committed automation, this index points to the documented UAT path and to deterministic API/static/build evidence that bounds the risk.

## Scope and requirements posture

M005 validation should be performed against the milestone roadmap success criteria rather than synthetic requirement IDs.

- Canonical milestone scope source: `.gsd/milestones/M005/M005-ROADMAP.md`
- Final integrated acceptance summary: `.gsd/milestones/M005/slices/S07/S07-SUMMARY.md`
- Tracked deterministic proof sources for validation:
  - `packages/webapp/tests/test_m005_final_learner_flow.py`
  - `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - `packages/webapp/docs/m005_s07_uat.md`
  - `packages/webapp/tests/verify_m005_s07_uat_doc.py`
  - `npm --prefix packages/webapp/frontend run build`

This posture keeps milestone validation evidence-based:

- roadmap success criteria are the acceptance contract;
- S01-S07 provide the shipped behavior and prior slice evidence;
- this document only indexes where that proof lives;
- future validation should cite package-local docs/tests/build output, not `.gsd/` internals, when explaining why a criterion passed or failed.

## Acceptance coverage matrix

| M005 success criterion | Primary proof | Supporting proof | Validation notes |
|---|---|---|---|
| Logged-in user reaches a main menu and can enter Continue Practice, Revision, Build Vocabulary, Analytics, Settings, or Log Out. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts authenticated menu labels and `activeSection` routing for `menu`, `practice`, `revision`, `build_vocabulary`, `analytics`, and `settings`. | `packages/webapp/tests/test_m005_final_learner_flow.py` covers registration/login and queue access for mixed, revision, and build-vocabulary modes. `packages/webapp/docs/m005_s07_uat.md` sections 2, 3, 8, 9, 11, 12, and 14 describe the visible learner walkthrough. | Deterministic proof exists for both UI contract markers and authenticated API flow. |
| Practice screen supports typed answer submit and Give Up, reveals correct answer, plays success/failure feedback, records events, and excludes analytics clutter. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts typed answer normalization, `/practice/answers` payload wiring, Give Up incorrect-recording path, `Correct` / `Not quite` result text, reveal copy, expected/submitted answer fields, and guards against client-computed correctness. | `packages/webapp/tests/test_m005_final_learner_flow.py` proves correct and wrong answers record backend events and update `/practice/progress`. `packages/webapp/docs/m005_s07_uat.md` sections 4, 5, 6, and 7 document typed correct, wrong, blank, and Give Up checks. | Audible success/failure remains browser/UAT-visible rather than fully committed E2E automation; API/static coverage proves event recording and diagnostic surfaces. |
| Queue modes enforce mixed, stale-only, and new-word-only behavior with ten-card base repeat gap where possible. | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts `mixed`, `revision`, and `build_vocabulary` queue mode payloads, `mode_detail`, queue membership, and `repeat_gap == 10`. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts the frontend issues the correct queue requests for all three modes. `packages/webapp/docs/m005_s07_uat.md` sections 3, 8, and 9 describe user-visible mode checks. | Revision-mode emptiness and build-vocabulary filtering are explicitly covered; the criterion is not inferred from prose alone. |
| Settings persist theme, default 0.8x TTS speed, and current single voice option; account deletion is confirmed and safely cascaded. | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts default settings payload, successful settings update, persistence across new client login, and delete-account rejection/success plus cascade cleanup of `users`, `user_settings`, `shown_cards`, and `answer_events`. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts settings load/save wiring, visible voice metadata, exact delete-confirmation phrase handling, and `DELETE /auth/account` request shape. `packages/webapp/docs/m005_s07_uat.md` sections 12 and 15 document reload/login persistence and deletion walkthroughs. | This criterion has both deterministic storage/API proof and user-visible UAT instructions. |
| Futuristic blue light/dark UI and repaired landing page meet static and accessibility-oriented checks. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts landing copy (`Welcome to MiraLingo`, `Wikibooks grammar`), safe external link attributes, dark-theme selectors, responsive breakpoints, `:focus-visible`, and major layout hooks. | `packages/webapp/docs/m005_s07_uat.md` section 1 documents the logged-out landing and external grammar link verification. `npm --prefix packages/webapp/frontend run build` proves the frontend compiles as shipped. | Validation should treat this as static/build-backed UI evidence, with browser walkthrough confirming the public landing surface. |
| Iconify icons render safely when available and degrade to neutral fallback without blocking practice. | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts bounded timeout, search limit, AbortController use, allowed icon-name validation, cache use, `<img>` rendering, visible `Iconify status`, and fallback/diagnostic surfaces. | `packages/webapp/tests/test_m005_final_learner_flow.py` covers the same learner flow while keeping product behavior safe if icon lookup is unavailable. `packages/webapp/docs/m005_s07_uat.md` section 13 documents matched-icon and forced offline/fallback checks. | Live Iconify availability depends on external network; validation should accept deterministic fallback/static evidence plus documented UAT for runtime observation. |
| API/unit/static frontend/integration evidence covers all final acceptance bullets. | `packages/webapp/tests/test_m005_final_learner_flow.py` is the integrated API/storage proof. `packages/webapp/tests/test_m005_frontend_assembly_static.py` is the final frontend assembly proof. `packages/webapp/tests/verify_m005_s07_uat_doc.py` is the UAT-document integrity proof. | `npm --prefix packages/webapp/frontend run build` is the production build proof. `packages/webapp/docs/m005_s07_uat.md` is the tracked manual/browser acceptance layer. | This is the milestone-wide evidence aggregation criterion; if any one artifact disappears, validation should fail the criterion rather than invent substitute proof. |

## Evidence inventory by acceptance area

### Auth, login, and learner menu

Primary evidence:

- `packages/webapp/tests/test_m005_final_learner_flow.py`
  - unauthenticated `/auth/current-user`, `/settings`, and `/practice/progress` all return structured `401` responses;
  - learner registration returns authenticated learner identity without secrets;
  - `GET /auth/current-user` returns authenticated learner identity after registration/login.
- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts menu labels for `Continue Practice`, `Revision`, `Build Vocabulary`, `Analytics`, `Settings`, and `Log Out`.
- `packages/webapp/docs/m005_s07_uat.md`
  - documents landing-page, registration, menu, logout, and logged-out reload checks.

### Practice answers, reveal flow, progress, and analytics separation

Primary evidence:

- `packages/webapp/tests/test_m005_final_learner_flow.py`
  - correct answer records `correct: true` event;
  - wrong answer records `correct: false` event;
  - `/practice/progress` exposes totals, accuracy, per-type summaries, latest event, weak/mastered counts, and card membership.
- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts typed answer trimming, backend-truth answer submission, Give Up path, reveal copy, and no practice-loop analytics fetch inside answer/queue paths.
- `packages/webapp/docs/m005_s07_uat.md`
  - documents correct, wrong, blank, Give Up, and analytics walkthrough checkpoints.

### Queue modes and repeat-gap behavior

Primary evidence:

- `packages/webapp/tests/test_m005_final_learner_flow.py`
  - mixed queue includes word and phrase cards in both directions;
  - revision queue can safely surface `empty_pool` when no revision cards are due;
  - build-vocabulary queue returns only new word cards;
  - repeat-gap payload includes `repeat_gap == 10`.
- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts the exact queue request URLs for mixed, revision, and build-vocabulary modes.

### Settings, voice metadata, audio behavior, and deletion safety

Primary evidence:

- `packages/webapp/tests/test_m005_final_learner_flow.py`
  - default settings show theme `system`, `tts_speed` `0.8`, and a single immutable MBROLA voice;
  - updated settings persist across a recreated client session;
  - audio success returns WAV bytes and diagnostic headers;
  - audio unavailable returns structured `503` JSON with `error == "mbrola_unavailable"`;
  - bad deletion confirmation is rejected without deleting the account;
  - successful deletion clears session and removes learner-owned rows.
- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts settings load/save request shapes, visible voice metadata labels, audio diagnostic/status roles, playback-rate fallback messaging, and exact delete-confirmation helpers.
- `packages/webapp/docs/m005_s07_uat.md`
  - documents manual audio observation limits, settings persistence walkthrough, deletion mismatch negative case, and successful deletion flow.

### Landing page, theme, and public link repair

Primary evidence:

- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts `Welcome to MiraLingo`, `Practice Mirad`, `Mirad learning lab`, `Mirad and MiraLingo docs`, the external `Wikibooks grammar` link, `_blank`/`noreferrer` attributes, dark theme selectors, responsive breakpoints, and focus-visible affordances.
- `packages/webapp/docs/m005_s07_uat.md`
  - documents logged-out landing verification and external grammar-link check.
- `npm --prefix packages/webapp/frontend run build`
  - ensures the shipped frontend compiles with the final landing/theme/icon code paths present.

### Iconify runtime and fallback behavior

Primary evidence:

- `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - asserts bounded Iconify fetch timeout (`ICONIFY_TIMEOUT_MS = 2500`), search limit, AbortController cleanup, collection validation, cache usage, visible status text, image markup, and fallback diagnostics.
- `packages/webapp/docs/m005_s07_uat.md`
  - documents two acceptable runtime observations: successful match when network is available, or safe fallback/offline behavior when Iconify is blocked.

## UAT evidence capture

The tracked browser/manual acceptance artifact is `packages/webapp/docs/m005_s07_uat.md`.

It explicitly captures or requests evidence for:

- logged-out landing and public `Wikibooks grammar` link;
- learner registration/login and authenticated menu;
- Continue Practice, Revision, and Build Vocabulary navigation;
- typed correct answer, wrong answer, blank answer, and Give Up reveal flow;
- audio button state plus success-or-diagnostic behavior;
- analytics/progress status;
- settings persistence across reload/login;
- Iconify matched-icon and forced fallback/offline behavior;
- logout and post-logout reload;
- account deletion mismatch and successful deletion.

The mechanical guard for the UAT artifact is `packages/webapp/tests/verify_m005_s07_uat_doc.py`, which fails if required sections or phrases disappear.

## Observability and diagnostics surfaces

These are the concrete surfaces a validator can inspect when an acceptance area fails or appears incomplete:

- `/auth/current-user`
  - logged-out structured `401` payload;
  - authenticated password-free learner payload.
- `/settings`
  - logged-out structured `401` payload with `phase: settings_get`;
  - authenticated settings payload with theme, speed, and voice metadata.
- `/practice/progress`
  - logged-out structured `401` payload with `phase: practice_progress`;
  - authenticated totals, accuracy, per-type summaries, latest event, and weak/mastered/new/stale counts.
- `/practice/audio/<card-id>`
  - deterministic WAV headers on success;
  - structured `503` JSON diagnostics on MBROLA-unavailable path.
- Frontend visible diagnostics asserted by static tests and documented by UAT:
  - `role="status"` surfaces;
  - `role="alert"` surfaces;
  - `Audio uses your saved ... learner speed preference`;
  - `Iconify status: ...`;
  - settings and account-deletion error/status copy.
- Safe SQLite inspection surfaces documented by UAT:
  - `users`
  - `user_settings`
  - `shown_cards`
  - `answer_events`

## Failure modes (Q5)

Validation should explicitly map common failure classes to the existing proof instead of inventing stronger runtime guarantees than the repository currently has.

| Failure mode | Existing proof | Validation posture |
|---|---|---|
| Logged-out API access breaks or leaks secrets | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts structured `401` payloads for `/auth/current-user`, `/settings`, and `/practice/progress`, plus no password/hash/salt/traceback leakage. | Treat as deterministic API regression coverage. |
| Wrong typed answer or Give Up path stops recording incorrect events | `packages/webapp/tests/test_m005_final_learner_flow.py` proves wrong-answer event recording and `/practice/progress` updates; `packages/webapp/tests/test_m005_frontend_assembly_static.py` proves Give Up submits backend `correct: false`. | Deterministic coverage exists. |
| Blank typed answer handling drifts | `packages/webapp/docs/m005_s07_uat.md` includes a dedicated blank-answer negative check. | Browser/manual UAT evidence required; no stronger deterministic backend proof is claimed here. |
| Deletion confirmation mismatch stops being safe | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts mismatched confirmation returns `400` and preserves login. `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts exact confirmation phrase helpers and request shape. | Deterministic proof exists for the safety gate. |
| Audio runtime is unavailable on the host | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts structured `mbrola_unavailable` `503` diagnostics. `packages/webapp/docs/m005_s07_uat.md` states audible playback may require manual observation. | Accept success-or-diagnostic behavior; do not require committed audible automation. |
| Iconify times out or the network is offline | `packages/webapp/tests/test_m005_frontend_assembly_static.py` asserts bounded timeout, fallback, and visible status. `packages/webapp/docs/m005_s07_uat.md` documents offline fallback as acceptable. | Accept safe fallback as pass when practice remains usable and diagnostics stay visible. |
| Stale or malformed session behavior appears after logout/deletion | `packages/webapp/tests/test_m005_final_learner_flow.py` asserts post-delete session teardown and failed relogin; `packages/webapp/docs/m005_s07_uat.md` documents logout/reload/session checks. | Deterministic proof exists for deletion teardown; logout reload remains documented UAT. |

Known evidence limit: the repository does not ship a committed browser E2E runner for this flow. Therefore live browser/audio/Iconify observations remain documented UAT evidence, not deterministic in-repo automation.

## Load profile (Q6)

Validation/documentation load introduced by this evidence index is trivial.

- This document adds no new runtime code path.
- It introduces no new shared resource, service, API call, queue, background worker, or persistence table.
- Validation cost is reading markdown plus rerunning already-existing deterministic tests and the frontend build.
- Runtime load claims remain inherited from S07 UAT documentation:
  - intended load is one local learner in one browser session;
  - shared resources are local SQLite, one browser cookie jar/session, optional Iconify public API requests, and optional local MBROLA runtime.

Validation should not attribute any new runtime load to S08/T01 itself.

## Negative-test coverage (Q7)

The milestone validator should be able to point to explicit evidence for these negative areas:

- wrong typed answer
  - `packages/webapp/tests/test_m005_final_learner_flow.py`
  - `packages/webapp/docs/m005_s07_uat.md`
- blank typed answer
  - `packages/webapp/docs/m005_s07_uat.md`
- deletion confirmation mismatch
  - `packages/webapp/tests/test_m005_final_learner_flow.py`
  - `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - `packages/webapp/docs/m005_s07_uat.md`
- logged-out API access
  - `packages/webapp/tests/test_m005_final_learner_flow.py`
  - `packages/webapp/docs/m005_s07_uat.md`
- Iconify timeout/offline fallback
  - `packages/webapp/tests/test_m005_frontend_assembly_static.py`
  - `packages/webapp/docs/m005_s07_uat.md`
- malformed or stale session evidence areas
  - `packages/webapp/docs/m005_s07_uat.md`
  - `packages/webapp/tests/test_m005_final_learner_flow.py` for deletion-triggered session teardown and invalid relogin

## Automation limits

The final validator should preserve the same automation limits already documented by S07 instead of overstating coverage.

- No committed Playwright/Cypress runner exists for the M005 learner flow.
- Browser automation/manual UAT is the intended proof layer above deterministic API/static/build tests.
- Audible success may depend on browser/device policy even when the backend audio endpoint is correct.
- Iconify live-match quality depends on public network access; safe fallback/offline behavior is an acceptable pass condition.
- Where runtime/browser behavior is not fully deterministic, validation should cite both:
  - the documented UAT step in `packages/webapp/docs/m005_s07_uat.md`; and
  - the deterministic bounded proof in `packages/webapp/tests/test_m005_final_learner_flow.py` or `packages/webapp/tests/test_m005_frontend_assembly_static.py`.

## Final validator checklist

Use this checklist when producing M005 milestone validation output:

1. Confirm this file exists and is non-empty.
2. Validate against M005 roadmap success criteria, not synthetic requirement IDs.
3. Cite `packages/webapp/tests/test_m005_final_learner_flow.py` for integrated auth, queue, settings, audio-diagnostic, progress, and deletion cascade evidence.
4. Cite `packages/webapp/tests/test_m005_frontend_assembly_static.py` for menu, landing, typed recall, settings UI, voice metadata, theme/accessibility hooks, and Iconify fallback/static contracts.
5. Cite `packages/webapp/docs/m005_s07_uat.md` for browser/manual evidence capture and explicit runtime limitations.
6. Cite `packages/webapp/tests/verify_m005_s07_uat_doc.py` to show the UAT artifact is mechanically guarded.
7. Cite `npm --prefix packages/webapp/frontend run build` as the production frontend assembly proof.
8. If browser/audio/Iconify live-runtime proof is incomplete, record the limitation explicitly and rely on the documented success-or-diagnostic and fallback acceptance posture rather than inventing certainty.
9. If any acceptance row above lacks a concrete tracked file or command, fail validation and name the missing evidence area directly.

## Verification commands referenced by this index

- `PYTHONPATH=packages/webapp/src python3 -m pytest packages/webapp/tests/test_m005_final_learner_flow.py -q`
- `PYTHONPATH=packages/webapp/src python3 -m pytest packages/webapp/tests/test_m005_frontend_assembly_static.py -q`
- `PYTHONPATH=packages/webapp/src python3 packages/webapp/tests/verify_m005_s07_uat_doc.py`
- `npm --prefix packages/webapp/frontend run build`

These commands are the concrete proof handles a future validator can rerun or cite.