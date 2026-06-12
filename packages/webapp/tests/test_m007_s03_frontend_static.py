from pathlib import Path

FRONTEND_ROOT = Path("packages/webapp/frontend/src")
LEARNING_ROOT = FRONTEND_ROOT / "lib" / "components" / "learning"
LAYOUT_ROOT = FRONTEND_ROOT / "lib" / "components" / "layout"
PAGES_ROOT = FRONTEND_ROOT / "lib" / "pages"
APP_FILE = FRONTEND_ROOT / "App.svelte"
DASHBOARD_PAGE = PAGES_ROOT / "Dashboard.svelte"
LEXICON_PAGE = PAGES_ROOT / "Lexicon.svelte"
WELCOME_PAGE = PAGES_ROOT / "Welcome.svelte"
PRIVACY_PAGE = PAGES_ROOT / "PrivacyPolicy.svelte"
PRIVACY_MARKDOWN = FRONTEND_ROOT / "lib" / "content" / "privacy-policy.md"
EXERCISE_CARD = LEARNING_ROOT / "ExerciseCard.svelte"
APP_SHELL = LAYOUT_ROOT / "AppShell.svelte"
STUDY_SHELL = LAYOUT_ROOT / "StudyShell.svelte"


def test_slice_components_exist() -> None:
    for path in [APP_FILE, DASHBOARD_PAGE, LEXICON_PAGE, WELCOME_PAGE, PRIVACY_PAGE, PRIVACY_MARKDOWN, EXERCISE_CARD, APP_SHELL, STUDY_SHELL]:
        assert path.exists(), f"expected {path} to exist"


def test_dashboard_copy_matches_today_surface() -> None:
    source = DASHBOARD_PAGE.read_text()
    assert "Continue Practice" in source
    assert "Revision" in source
    assert "Build Vocabulary" in source
    assert "Lexicon Search" in source
    assert "Your next Mirad study actions" in source


def test_welcome_copy_matches_logged_out_surface() -> None:
    source = WELCOME_PAGE.read_text()
    assert "Welcome to Mirad" in source
    assert "Create Account" in source
    assert "Log In" in source
    assert "By creating an account, you agree to the" in source
    assert 'href="#privacy"' in source


def test_privacy_policy_page_and_markdown_contract() -> None:
    app_source = APP_FILE.read_text()
    page_source = PRIVACY_PAGE.read_text()
    markdown_source = PRIVACY_MARKDOWN.read_text()

    assert "What we do not do" in markdown_source
    assert "MiraLingo does not sell your personal information" in markdown_source
    assert "Account information" in markdown_source
    assert "Practice activity" in markdown_source
    assert "import PrivacyPolicy from \"./lib/pages/PrivacyPolicy.svelte\";" in app_source
    assert 'routeHash === "privacy"' in app_source
    assert "privacy-policy.md?raw" in page_source
    assert "Clear notes on account data" in page_source


def test_lexicon_tts_preserves_full_comma_separated_translation() -> None:
    source = LEXICON_PAGE.read_text()
    assert 'function getPreviewMiradText(result: LookupResult): string {' in source
    assert ".replace(/\\s*,\\s*/g, ', ')" in source
    assert '.split(/[;,|/]/g)' not in source
    assert 'await playMbrolaPreview(previewText, speakingWord, token);' in source


def test_tts_buttons_show_playing_state_and_toggle_stop() -> None:
    app_source = APP_FILE.read_text()
    audio_button_source = (LEARNING_ROOT / "AudioButton.svelte").read_text()
    lexicon_source = LEXICON_PAGE.read_text()

    assert 'playing={audioPlaying}' in (LEARNING_ROOT / "ExercisePrompt.svelte").read_text()
    assert 'playing={audioPlaying}' in (LEARNING_ROOT / "FeedbackPanel.svelte").read_text()
    assert 'audioPlaying={audioState === "playing"}' in app_source
    assert 'if (audioState === "playing" && activeAudio)' in app_source
    assert 'audioState = "playing";' in app_source
    assert "aria-pressed={playing}" in audio_button_source
    assert "playing ? '■' : '🔊'" in audio_button_source
    assert "audio-button-playing" in audio_button_source
    assert "background: #7c3aed !important;" in audio_button_source
    assert 'if (speakingWord === activeWord)' in lexicon_source
    assert 'resetPreviewAudio();' in lexicon_source


def test_app_routes_through_pages_and_shells() -> None:
    source = APP_FILE.read_text()
    assert 'import Dashboard from "./lib/pages/Dashboard.svelte";' in source
    assert 'import Welcome from "./lib/pages/Welcome.svelte";' in source
    assert 'import AppShell from "./lib/components/layout/AppShell.svelte";' in source
    assert 'import StudyShell from "./lib/components/layout/StudyShell.svelte";' in source
    assert 'import ExerciseCard from "./lib/components/learning/ExerciseCard.svelte";' in source
    assert '<Dashboard' in source
    assert '<Welcome' in source
    assert '<AppShell' in source
    assert '<StudyShell' in source
    assert '<ExerciseCard' in source


def test_app_is_section_router_not_legacy_inline_surfaces() -> None:
    source = APP_FILE.read_text()
    assert 'import { currentSection' in source
    assert 'practiceSection($currentSection)' in source
    assert 'navigateToSection("practice")' in source
    assert 'syncRouteFromHash' in source
    assert 'shell shell--practice' not in source
    assert 'menu-btns' not in source
    assert 'settings-form' not in source
