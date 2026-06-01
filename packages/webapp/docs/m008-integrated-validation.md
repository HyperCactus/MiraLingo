# M008 Integrated Validation Evidence

This document maps each M008 acceptance criterion to executable evidence and inspection surfaces.
It is a validation map, not an implementation spec.

## Command Set (root-relative)

- `PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_m008_integrated_learner_flow.py -q`
- `PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_m008_analytics_api.py packages/webapp/tests/test_m008_weighted_queue_policy.py packages/webapp/tests/test_m008_practice_api_compatibility.py -q`
- `PYTHONPATH=packages/webapp/src python -m pytest packages/webapp/tests/test_analytics_ui_static.py packages/webapp/tests/test_progress_ui_static.py -q`
- `npm --prefix packages/webapp/frontend run build` (build definition in `packages/webapp/frontend/package.json`)

## Acceptance Matrix

| # | Acceptance Criterion | Automated Evidence | Manual / UAT Evidence | Failure Surface |
|---|---|---|---|---|
| 1 | Durable authenticated session + lifecycle storage across multiple learner sessions | `packages/webapp/tests/test_m008_integrated_learner_flow.py` validates `/practice/sessions/start`, `/practice/sessions/end`, persisted session rows, and lifecycle state continuity. | Verify local login/logout/session continuity in browser (see UAT checklist). | API responses from `/practice/sessions*`; persisted SQLite-backed state through storage/API behavior. |
| 2 | Promotion to revision after 4 correct answers across 2 sessions, plus deterministic demotion/regression behavior | `packages/webapp/tests/test_m008_integrated_learner_flow.py` verifies promotion (`correct_streak >= 4`, `session_streak >= 2`, lifecycle `revision`). Regression/direction sparsity is checked via direction breakdown and wrong-answer path. | Observe learner progress trend in UI over repeated sessions; confirm behavior is understandable to operator. | `/practice/answers` payloads, lifecycle counters, analytics lifecycle breakdown. |
| 3 | Weighted queue targets + small-pool diagnostics | `packages/webapp/tests/test_m008_weighted_queue_policy.py` validates requested vs actual ratios/mix, repeat-gap behavior, weighting inputs, and `small_pool` fallback reasons. Integrated flow test also checks diagnostics keys + fallback reasons. | In local UAT, inspect queue behavior under limited card set and confirm fallback messaging/state does not break navigation. | `/practice/queue` JSON diagnostics (`fallback_reasons`, ratio/mix drift, repeat-gap fields). |
| 4 | Compact `/practice/progress` compatibility while analytics provides detailed drill-down | `packages/webapp/tests/test_m008_practice_api_compatibility.py` and `packages/webapp/tests/test_m008_analytics_api.py` pin compact progress envelope and detailed analytics payloads, including sparse and malformed-event-safe behavior. | Use dashboard/analytics navigation checklist to ensure compact and detailed views remain understandable. | `/practice/progress` JSON (`event_count`, `latest_event`, `per_type`, `per_direction`) and `/practice/analytics` JSON (`direction_breakdown`, `sparse_history`, per-card/session summaries). |
| 5 | Dashboard summary + analytics frontend behavior, including sparse/error states | `packages/webapp/tests/test_analytics_ui_static.py` and `packages/webapp/tests/test_progress_ui_static.py` pin route ownership, helper usage, and error/sparse markers. | Browser UAT required for visual and interaction proof (documented below; manual evidence). | Frontend sparse/error UI states; analytics route navigation and dashboard summary surfaces. |
| 6 | Focused regression coverage + frontend build + final integrated learner flow | Command set above covers focused backend regressions, frontend static assertions, build integrity, and final integrated learner-loop test. | Manual browser UAT remains required because there is no committed browser E2E runner in this package. | Pytest command outputs and frontend build output are the primary pass/fail surfaces. |

## Negative-Test Evidence Rows (Q7)

- Sparse history/new learner: `test_practice_analytics_starts_sparse_for_new_learner` (`packages/webapp/tests/test_m008_analytics_api.py`).
- Small-card-pool fallback and drift diagnostics: `test_weighted_queue_small_pool_reports_drift_and_repeat_gap_relaxation_reasons` (`packages/webapp/tests/test_m008_weighted_queue_policy.py`).
- Auth gating: `test_practice_analytics_requires_authenticated_session` and `test_session_control_requires_authentication`.
- Malformed/non-ok analytics fallback and validation safety: `test_practice_analytics_invalid_filters_and_malformed_events_are_safe` and `test_practice_analytics_missing_content_source_returns_structured_payload`.
- Compact progress compatibility: `test_progress_api_is_not_fetched_from_primary_practice_loop`, `test_dashboard_owns_progress_helper_call`, and `test_practice_progress_compact_contract_remains_compatible`.

## Manual Local UAT Checklist (documented manual evidence)

This section is a manual follow-up checklist, not automated proof.

1. Login/auth gating
   - Confirm logged-out access to learner API surfaces yields auth-gated responses.
   - Confirm login allows dashboard + practice + analytics navigation.
2. Dashboard summary behavior
   - Confirm dashboard shows compact progress-oriented summary signals.
   - Confirm summary refresh remains stable while practicing.
3. Analytics navigation and drill-down
   - Navigate to analytics view and confirm it renders detailed breakdown data.
   - Confirm sparse-history state is clearly surfaced for a new/low-history learner.
4. Sparse/error frontend states
   - Confirm malformed/non-ok analytics responses render safe fallback UI (no stacktrace).
   - Confirm queue small-pool conditions do not crash navigation.
5. Practice navigation continuity
   - Start practice, answer multiple cards, and verify progression without route dead-ends.

## Failure Modes and Interpretation (Q5)

- If a backend pytest command fails, do not treat M008 acceptance as complete; inspect the failing API/test surface named in the pytest output.
- If frontend static pytest fails, treat the related dashboard/analytics UI acceptance row as unproven.
- If `npm --prefix packages/webapp/frontend run build` fails, frontend assembly acceptance remains unproven.
- If manual browser UAT is not run, UI interaction claims remain manual follow-up evidence only.

## Evidence Scope Guardrails

- Evidence paths must remain committed project files under `packages/webapp/**`.
- `.gsd/`, temporary local artifacts, and gitignored files are not accepted as completion proof for M008 validation.
