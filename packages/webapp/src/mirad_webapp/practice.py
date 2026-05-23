"""Public practice scheduler API.

This module is the stable import surface for the adaptive practice engine.  The
implementation lives in :mod:`mirad_webapp.practice_engine` so earlier tests and
API handlers that imported that name continue to work during the S03 rollout.
"""

from __future__ import annotations

from mirad_webapp.practice_engine import (
    MAX_EVENTS,
    STALE_AFTER_SECONDS,
    answer_summary,
    build_practice_progress,
    build_practice_queue,
    record_practice_answer,
    stable_card_id,
)

__all__ = [
    "MAX_EVENTS",
    "STALE_AFTER_SECONDS",
    "answer_summary",
    "build_practice_progress",
    "build_practice_queue",
    "record_practice_answer",
    "stable_card_id",
]
