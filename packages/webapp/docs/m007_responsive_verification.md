# M007 S05 responsive verification

Verified practice/settings/navigation usability across target breakpoints after T04 polish.

## Viewports checked

- 375×812 (mobile)
- 430×932 (mobile large)
- 768×1024 (tablet)
- 1280×800 (desktop)

## Checks

1. Practice surface actions (Submit answer, Show answer/Continue, audio action) stay visible in a single viewport without page scrolling.
2. Bottom navigation targets remain tappable at mobile breakpoints.
3. Settings controls (theme radios, TTS speed radios, autoplay checkbox, save button) remain usable and reachable.

## Notes

- Exercise actions retain `min-h-12` touch targets.
- Updated label uses "Show answer" (no "Give up" strings remain in app/learning components).
- Static assembly test now validates split page/component layout rather than legacy monolithic App.svelte internals.

## 2026-06-01 live validation attempt

Live browser verification was executed against local API (`127.0.0.1:8000`) and Vite frontend (`127.0.0.1:4173`).

- Welcome screen rendered and remained navigable at 375/430/768/1280 widths.
- Account creation succeeded and routed to `#dashboard`.
- Practice navigation reached `#practice`, but practice content requests returned repeated `502` responses (`CardContent...` backend import failure surfaced in UI).

Because practice data failed to load during this run, the full acceptance flow (answer/check/show/continue-without-scroll at 375px) could not be re-proven live in this environment.
