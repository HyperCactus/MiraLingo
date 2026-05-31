# M007 Frontend Audit: `App.svelte`

## Auth state management
- `authState` drives `checking`, `anonymous`, `authenticated`, `login-failed`, and `registration-failed` screen states.
- Session bootstrap runs through `loadCurrentUser()` on module load, then resets practice/settings/analytics surfaces and preloads mixed practice after successful auth.
- Login, registration, logout, and account deletion all mutate shared top-level app state directly; success paths also repopulate `deleteAccountUsername` and reload settings.

## Practice mode state
- Practice uses `practiceState`, `practiceQueue`, `practiceQueueCards`, `practiceQueueIndex`, `practiceQueueMode`, `currentCard`, `typedAnswer`, `answerResult`, and `miradAudioUnlocked` as one coupled state cluster.
- `openPracticeMode()`, `loadPracticeQueue()`, `advancePracticeCard()`, and `recordAnswer()` together own queue lifecycle, answer submission, and card transitions.
- Audio gating depends on card direction: English→Mirad answers unlock Mirad playback only after reveal.

## Settings state
- Settings are split between `settingsForm` (editable draft) and `persistedSettings` (last saved payload), normalized through `coercePayload()` and `syncSettings()`.
- `settingsState`, `settingsErr`, `settingsStatus`, and `settingsPhase` track fetch/save lifecycle.
- Delete-account fields live beside user settings in the same top-level component state and are reset together by `resetSettingsSurface()`.

## Current section and screen navigation
- `activeSection` switches between `menu`, `practice`, `revision`, `build_vocabulary`, `analytics`, and `settings`.
- The authenticated shell is currently implemented as a single large conditional template in `App.svelte`; each section branch owns its own top bar, body layout, and action wiring.
- `activateItem()` mixes route-like navigation with side effects such as `loadAnalytics()`, `loadSettings()`, and `logout()`.

## TTS handling
- `playCardAudio()` fetches `/practice/audio/:cardId`, inspects content type to detect JSON error payloads, and creates an `Audio` object from a blob URL.
- `resetAudio()` is responsible for stopping playback and revoking blob URLs.
- Effective playback speed is derived from `settingsForm.tts_speed`, so unsaved UI changes already affect playback behavior.

## Iconify usage
- Icon lookup is entirely inline: keyword extraction, allowlisted collections, timeout handling, search fetch, fallback state, cache key generation, and icon rendering all live in `App.svelte`.
- The component calls the public Iconify search API directly with a 2.5 second timeout and caches results in `iconCache` keyed by practice card identity.
- Icon state is tracked separately from practice state (`icStatus`, `icErr`, `icImg`, `icAlt`, `icMeta`, `icLk`) but still managed from the same root component.

## Refactor pressure points for S02+
- `App.svelte` currently mixes API clients, state orchestration, route/view switching, media handling, and presentation markup in one file.
- Practice, analytics, and settings sections already have clean enough boundaries to extract into shells/components once API and store modules exist.
- The local Vite proxy currently exposes backend routes as `/auth`, `/practice`, `/settings`, and `/content` rather than a shared `/api` prefix, so frontend extraction should preserve those existing route shapes unless proxy config changes later.
