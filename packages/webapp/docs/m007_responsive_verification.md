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
