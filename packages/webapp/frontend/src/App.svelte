<script>
  import { onMount } from "svelte";
  import "./app.css";
  import { getPracticeAudioUrl } from "./lib/api/audio";
  import { deleteAccount, fetchCurrentUser, login, logout as logoutRequest, readJson, register, requestPasswordReset, resetPassword } from "./lib/api/auth";
  import { getPracticeQueue, submitPracticeAnswer } from "./lib/api/practice";
  import { getSettings, updateSettings } from "./lib/api/settings";
  import AppShell from "./lib/components/layout/AppShell.svelte";
  import StudyShell from "./lib/components/layout/StudyShell.svelte";
  import ExerciseCard from "./lib/components/learning/ExerciseCard.svelte";
  import LexiconBubble from "./lib/components/learning/LexiconBubble.svelte";
  import { lookupExact, lookupWord } from "./lib/api/lookup";
  import AppButton from "./lib/components/ui/AppButton.svelte";
  import AppCard from "./lib/components/ui/AppCard.svelte";
  import AppInput from "./lib/components/ui/AppInput.svelte";
  import { authError, authMessage, authState, currentUser, resetAuthStore, setAnonymous, setAuthenticated, setAuthFailure } from "./lib/stores/auth";
  import { currentSection, goToDashboard, resetPracticeNavigation, setCurrentSection, setPracticeMode } from "./lib/stores/practice";
  import { applySettingsPayload, resetSettingsStore, settingsLoadedForUser, soundEffectsMode, theme, ttsSpeed } from "./lib/stores/settings";
  import Dashboard from "./lib/pages/Dashboard.svelte";
  import AdminDashboard from "./lib/pages/AdminDashboard.svelte";
  import Analytics from "./lib/pages/Analytics.svelte";
  import Lexicon from "./lib/pages/Lexicon.svelte";
  import ResetPassword from "./lib/pages/ResetPassword.svelte";
  import Welcome from "./lib/pages/Welcome.svelte";

  const PASSWORD_MIN_LENGTH = 8;
  const PASSWORD_MAX_LENGTH = 128;
  const PASSWORD_RULE_MESSAGE = `Password must be ${PASSWORD_MIN_LENGTH} to ${PASSWORD_MAX_LENGTH} characters.`;
  const ADMIN_ACCOUNT_EMAIL = "sampollard888@gmail.com";
  const fmtPct = (value) => (typeof value === "number" ? `${Math.round(value * 100)}%` : "—");
  const fmtN = (value) => (typeof value === "number" ? value : "—");
  const spd = (value) => `${Number(value).toFixed(1)}×`;
  const coerceTheme = (value) => (["light", "dark"].includes(value) ? value : "system");
  const coerceSpeed = (value) => {
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) && parsed >= 0.5 && parsed <= 2.0 ? parsed : 0.8;
  };
  const practiceSection = (section) => section === "practice" || section === "revision" || section === "build_vocabulary";
  const practiceTitle = (section) => (
    section === "revision" ? "Revision" : section === "build_vocabulary" ? "Vocabulary" : "Practice"
  );
  const emptyPracticeMessage = (mode) => {
    if (mode === "revision") return "Nothing to revise yet. Go to Practice or Build Vocabulary to learn new words.";
    if (mode === "build_vocabulary") return "No new vocabulary is ready right now. Try Practice or Revision instead.";
    return "No practice cards are ready right now.";
  };
  const navItemsFor = (section) => {
    const items = [
      { id: "dashboard", label: "Today", href: "#dashboard", active: section === "dashboard" },
      { id: "practice", label: "Practice", href: "#practice", active: practiceSection(section) },
      { id: "lexicon", label: "Lexicon", href: "#lexicon", active: section === "lexicon" },
      { id: "settings", label: "Settings", href: "#settings", active: section === "settings" },
    ];
    if (isAdminUser($currentUser)) {
      items.push({ id: "admin", label: "Admin", href: "#admin", active: section === "admin" });
    }
    return items;
  };
  const soundEffectsEnabledFromMode = (mode) => mode === "all" || mode === "on_answer";
  const uiButtonSoundsEnabledFromMode = (mode) => mode === "all" || mode === "ui_only";
  const sfxModeFromToggles = (uiButtonsEnabled, effectsEnabled) => {
    if (uiButtonsEnabled && effectsEnabled) return "all";
    if (uiButtonsEnabled) return "ui_only";
    if (effectsEnabled) return "on_answer";
    return "off";
  };

  const displayName = (user) => user?.name || user?.email || "Learner";
  const isAdminUser = (user) => String(user?.email ?? "").trim().toLowerCase() === ADMIN_ACCOUNT_EMAIL;
  const normalizeAnswer = (value) => String(value ?? "").trim().toLowerCase().replace(/[\s.,!?;:"'’‘“”()[\]{}-]+/g, " ").trim();
  const answerMatchesCard = (card, answer) => {
    const submitted = normalizeAnswer(answer);
    const expected = normalizeAnswer(card?.answer);
    if (!submitted || !expected) return false;
    const alternatives = String(card?.answer ?? "")
      .split(/[,;|/]+/)
      .map(normalizeAnswer)
      .filter(Boolean);
    return submitted === expected || alternatives.includes(submitted);
  };
  const optimisticAnswerResult = (card, answer, correct = null) => ({
    ok: true,
    expected_answer: card?.answer ?? "",
    submitted_answer: answer ?? "",
    correct: correct === null ? answerMatchesCard(card, answer) : Boolean(correct),
    pending: true,
  });

  let loginEmail = $state("");
  let password = $state("");
  let registrationEmail = $state("");
  let registrationName = $state("");
  let regP = $state("");
  let resetToken = $state("");
  let resetNewPassword = $state("");
  let resetConfirmPassword = $state("");
  let resetError = $state("");
  let resetMessage = $state("");
  let resetSubmitting = $state(false);
  let submitting = $state(false);

  let practiceState = $state("idle");
  let practiceErr = $state("");
  let practiceQueueCards = $state([]);
  let practiceQueueIndex = $state(0);
  let practiceQueueMode = $state(null);
  let prefetchedPracticeQueues = new Map();
  let practicePreloadPromises = new Map();
  let currentCard = $state(null);
  let typedAnswer = $state("");
  let answerErr = $state("");
  let answerSubmitting = $state(false);
  let answerResult = $state(null);
  let activeAchievement = $state(null);
  let miradAudioUnlocked = $state(false);
  let activeCardId = $state(null);
  /** Prevents a resolved recordAnswer from overwriting state after the user moved to a new card. */
  let currentSubmissionCardId = $state(null);

  let audioState = $state("idle");
  let audioMsg = $state("");
  let audioBlobUrl = $state("");
  let activeAudio = $state(null);
  let lastAudioCardId = $state(null);
  let lastAutoplayRevealCardId = $state(null);


  let settingsState = $state("idle");
  let settingsErr = $state("");
  let settingsStatus = $state("");
  let settingsPhase = $state("");
  let ttsAutoplayEnabled = $state(true);
  let dashboardRefreshSignal = $state(0);
  let dashboardRefreshTimer = null;

  let soundEffectsInfoOpen = $state(false);
  let deleteAccountState = $state("idle");
  let deleteAccountErr = $state("");
  let deleteAccountStatus = $state("");
  let deleteAccountConfirm = $state("");
  let deleteAccountEmail = $state("");

  // Lexicon bubble state
  let bubbleResults = $state([]);
  let bubbleVisible = $state(false);
  let bubbleAnchorRect = $state(null);
  let bubbleDirection = $state('en_to_mir');
  let bubbleLoading = $state(false);
  let bubbleError = $state('');

  function replaceHash(section) {
    if (typeof window === "undefined") return;
    window.history.replaceState(null, "", `#${section}`);
  }

  function resolveTheme(themeValue) {
    if (themeValue === "light" || themeValue === "dark") return themeValue;
    if (typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  function applyTheme(themeValue) {
    if (typeof document === "undefined") return;
    const resolvedTheme = resolveTheme(coerceTheme(themeValue));
    document.documentElement.setAttribute("data-theme", resolvedTheme);
    document.documentElement.classList.toggle("dark", resolvedTheme === "dark");
  }

  function readResetTokenFromUrl() {
    if (typeof window === "undefined") return "";
    return new URLSearchParams(window.location.search).get("reset_token")?.trim() ?? "";
  }

  function clearResetUrl() {
    if (typeof window === "undefined") return;
    window.history.replaceState(null, "", `${window.location.pathname}#welcome`);
  }

  function resetPasswordFormState() {
    resetNewPassword = "";
    resetConfirmPassword = "";
    resetError = "";
  }

  function passwordLengthValid(value) {
    return value.length >= PASSWORD_MIN_LENGTH && value.length <= PASSWORD_MAX_LENGTH;
  }

  const resetAudio = () => {
    if (activeAudio) {
      activeAudio.pause();
      activeAudio = null;
    }
    if (audioBlobUrl) {
      URL.revokeObjectURL(audioBlobUrl);
      audioBlobUrl = "";
    }
    audioState = "idle";
    audioMsg = "";
    // Clear stale preloaded audio if it no longer matches the current card.
    const currentAudioCardId = currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id;
    if (preloadedCardId && preloadedCardId !== currentAudioCardId) {
      if (preloadedAudio) {
        URL.revokeObjectURL(preloadedAudio.blobUrl);
      }
      preloadedAudio = null;
      preloadedCardId = null;
    }
  };

  const resetAnswer = () => {
    typedAnswer = "";
    answerErr = "";
    answerResult = null;
    activeAchievement = null;
    miradAudioUnlocked = false;
  };

  const resetPracticeSurface = () => {
    resetAudio();
    resetAnswer();
    practiceState = "idle";
    practiceErr = "";
    practiceQueueCards = [];
    practiceQueueIndex = 0;
    practiceQueueMode = null;
    prefetchedPracticeQueues.clear();
    practicePreloadPromises.clear();
    currentCard = null;
    activeCardId = null;
    lastAudioCardId = null;
  };


  const resetSettingsSurface = () => {
    settingsState = "idle";
    settingsErr = "";
    settingsStatus = "";
    settingsPhase = "";
    settingsSaveEnabled = false;
    resetSettingsStore();
    deleteAccountState = "idle";
    deleteAccountErr = "";
    deleteAccountStatus = "";
    deleteAccountEmail = "";
    deleteAccountConfirm = "";
  };

  const syncSettings = (payload, extra = {}) => {
    applySettingsPayload(payload ?? {});
    ttsAutoplayEnabled = Boolean(payload?.tts_autoplay ?? true);
    if (payload?.sfx_mode) {
      soundEffectsMode.set(payload.sfx_mode);
    } else {
      soundEffectsMode.set(Boolean(payload?.sfx_enabled ?? true) ? 'on_answer' : 'off');
    }
    if (extra.state) settingsState = extra.state;
    if (extra.phase) settingsPhase = extra.phase;
    settingsSaveEnabled = true;
  };

  async function loadCurrentUser() {
    authError.set("");
    try {
      const { response, payload } = await fetchCurrentUser();
      if (response.ok && payload.authenticated && payload.user) {
        setAuthenticated(payload.user);
        resetPracticeSurface();
        resetSettingsSurface();
        deleteAccountEmail = payload.user.email ?? "";
        await loadSettings({ force: true });
        await preloadPracticeQueue("mixed");
        syncRouteFromHash("dashboard");
        return;
      }
      setAnonymous();
      resetSettingsSurface();
      resetPracticeNavigation();
      replaceHash("welcome");
    } catch (_) {
      setAnonymous();
      resetSettingsSurface();
      resetPracticeNavigation();
      authError.set("Could not reach MiraLingo auth.");
    }
  }

  async function submitLogin() {
    submitting = true;
    authError.set("");
    try {
      const { response, payload } = await login(loginEmail, password);
      if (!response.ok || !payload.authenticated || !payload.user) {
        setAuthFailure("login-failed", payload?.detail ?? "Login failed.");
        return;
      }
      setAuthenticated(payload.user);
      password = "";
      resetPracticeSurface();
      resetSettingsSurface();
      deleteAccountEmail = payload.user.email ?? "";
      await loadSettings({ force: true });
      await preloadPracticeQueue("mixed");
      navigateToSection("dashboard");
    } catch (_) {
      setAuthFailure("login-failed", "Could not reach MiraLingo auth.");
    } finally {
      submitting = false;
    }
  }

  async function submitPasswordResetRequest() {
    const email = loginEmail.trim();
    if (!email) {
      authError.set("Enter your email first, then request a password reset.");
      authMessage.set("");
      return;
    }
    submitting = true;
    authError.set("");
    authMessage.set("");
    try {
      const { response, payload } = await requestPasswordReset(email);
      if (!response.ok) {
        authError.set(payload?.detail ?? "Could not request password reset.");
        return;
      }
      authMessage.set(payload?.detail ?? "If an account exists, reset instructions have been sent.");
    } catch (_) {
      authError.set("Could not request password reset.");
      authMessage.set("");
    } finally {
      submitting = false;
    }
  }

  async function submitRegistration() {
    if (!passwordLengthValid(regP)) {
      setAuthFailure("registration-failed", PASSWORD_RULE_MESSAGE);
      return;
    }
    submitting = true;
    authError.set("");
    try {
      const { response, payload } = await register(registrationEmail, regP, registrationName);
      if (!response.ok || !payload.authenticated || !payload.user) {
        setAuthFailure("registration-failed", payload?.detail ?? "Registration failed.");
        return;
      }
      setAuthenticated(payload.user);
      regP = "";
      resetPracticeSurface();
      resetSettingsSurface();
      deleteAccountEmail = payload.user.email ?? "";
      await loadSettings({ force: true });
      await preloadPracticeQueue("mixed");
      navigateToSection("dashboard");
    } catch (_) {
      setAuthFailure("registration-failed", "Could not reach MiraLingo registration.");
    } finally {
      submitting = false;
    }
  }

  async function submitPasswordReset() {
    if (!resetToken) {
      resetError = "Password reset link is missing or invalid. Request a new reset email.";
      resetMessage = "";
      return;
    }
    if (!passwordLengthValid(resetNewPassword)) {
      resetError = PASSWORD_RULE_MESSAGE;
      resetMessage = "";
      return;
    }
    if (resetNewPassword !== resetConfirmPassword) {
      resetError = "Passwords do not match.";
      resetMessage = "";
      return;
    }

    resetSubmitting = true;
    resetError = "";
    resetMessage = "";
    try {
      const { response, payload } = await resetPassword(resetToken, resetNewPassword);
      if (!response.ok || payload.ok === false) {
        resetError = payload?.detail ?? "Could not reset password.";
        return;
      }
      resetToken = "";
      resetPasswordFormState();
      clearResetUrl();
      resetAuthStore("Password reset. Log in with your new password.");
    } catch (_) {
      resetError = "Could not reset password.";
    } finally {
      resetSubmitting = false;
    }
  }

  function cancelPasswordReset() {
    resetToken = "";
    resetMessage = "";
    resetPasswordFormState();
    clearResetUrl();
    resetAuthStore();
  }

  function clearAuthAppState(message = "") {
    resetPracticeSurface();
    resetSettingsSurface();
    loginEmail = "";
    password = "";
    registrationEmail = "";
    regP = "";
    resetPracticeNavigation();
    resetAuthStore(message);
    replaceHash("welcome");
  }

  async function logout() {
    clearAuthAppState();
    try {
      await logoutRequest();
    } catch (_) {
      // UI is already logged out; a failed revoke request should not strand the user on an authenticated page.
    }
  }

  async function loadSettings({ force = false } = {}) {
    if (settingsState === "loading" || settingsState === "saving") return;
    if (!force && $settingsLoadedForUser === $currentUser?.id && settingsState !== "idle") return;

    settingsState = "loading";
    settingsErr = "";
    settingsStatus = "";

    try {
      const { response, payload } = await getSettings();
      if (!response.ok || payload.ok === false) {
        settingsState = "error";
        settingsPhase = payload?.phase ?? "settings_get";
        settingsErr = payload?.detail ?? "Could not reach saved settings.";
        return;
      }
      syncSettings(payload.settings, { state: "ready", phase: payload.phase ?? "settings_get" });
      settingsLoadedForUser.set($currentUser?.id ?? null);
    } catch (_) {
      settingsLoadedForUser.set($currentUser?.id ?? null);
      applySettingsPayload({});
      settingsState = "error";
      settingsPhase = "settings";
      settingsErr = "Could not reach saved settings.";
    }
  }

  let settingsSaveEnabled = $state(false);

  async function saveSettings() {
    if (!settingsSaveEnabled || !$currentUser?.id || settingsState === "saving") return;
    settingsState = "saving";
    try {
      const body = {
        theme: coerceTheme($theme),
        tts_speed: coerceSpeed($ttsSpeed),
        tts_autoplay: Boolean(ttsAutoplayEnabled),
        sfx_enabled: soundEffectsEnabledFromMode($soundEffectsMode),
        sfx_mode: $soundEffectsMode,
      };
      await updateSettings(body);
      settingsState = "ready";
    } catch (_) {
      settingsState = "ready";
    }
  }

  function setUiButtonSounds(enabled) {
    soundEffectsMode.set(sfxModeFromToggles(Boolean(enabled), soundEffectsEnabledFromMode($soundEffectsMode)));
    void saveSettings();
  }

  function setPracticeSoundEffects(enabled) {
    soundEffectsMode.set(sfxModeFromToggles(uiButtonSoundsEnabledFromMode($soundEffectsMode), Boolean(enabled)));
    void saveSettings();
  }

  function applyPracticeQueue(mode, cards) {
    practiceQueueCards = cards;
    practiceQueueIndex = 0;
    practiceQueueMode = mode;
    currentCard = cards[0] ?? null;
    practiceState = cards.length ? "ready" : "empty";
    practiceErr = cards.length ? "" : emptyPracticeMessage(mode);
    resetAnswer();
    resetAudio();
    warmNextPracticeQueue(mode);
  }

  async function fetchPracticeQueueCards(mode = "mixed") {
    const { response, payload } = await getPracticeQueue(mode, mode === "revision" ? 30 : mode === "build_vocabulary" ? 12 : 8);
    if (!response.ok || payload.ok === false) {
      const error = new Error(payload?.detail ?? "Could not load practice cards.");
      error.payload = payload;
      throw error;
    }
    return Array.isArray(payload.cards) ? payload.cards : [];
  }

  async function loadPracticeQueue(mode = "mixed", options = {}) {
    const silent = options.silent === true;
    if (!silent) {
      practiceState = "loading";
      practiceErr = "";
    }

    try {
      const cards = await fetchPracticeQueueCards(mode);
      if (silent) {
        prefetchedPracticeQueues.set(mode, cards);
        return cards;
      }
      applyPracticeQueue(mode, cards);
      return cards;
    } catch (error) {
      if (silent) return [];
      practiceState = "error";
      practiceErr = error?.payload?.detail ?? error?.message ?? "Could not load practice cards.";
      return [];
    }
  }

  function warmNextPracticeQueue(mode = "mixed") {
    if (!$currentUser?.id || practicePreloadPromises.has(mode)) return;
    const promise = loadPracticeQueue(mode, { silent: true })
      .catch(() => [])
      .finally(() => practicePreloadPromises.delete(mode));
    practicePreloadPromises.set(mode, promise);
  }

  async function preloadPracticeQueue(mode = "mixed") {
    if (prefetchedPracticeQueues.has(mode) || (practiceQueueMode === mode && practiceQueueCards.length > 0)) return;
    if (practicePreloadPromises.has(mode)) return practicePreloadPromises.get(mode);
    warmNextPracticeQueue(mode);
    return practicePreloadPromises.get(mode);
  }

  async function openPracticeMode(mode) {
    setPracticeMode(mode);
    replaceHash(mode === "mixed" ? "practice" : mode);

    const prefetched = prefetchedPracticeQueues.get(mode);
    if (prefetched) {
      prefetchedPracticeQueues.delete(mode);
      applyPracticeQueue(mode, prefetched);
      return;
    }

    if (practiceQueueMode === mode && practiceQueueCards.length > 0) {
      practiceState = "ready";
      currentCard = practiceQueueCards[practiceQueueIndex] ?? practiceQueueCards[0] ?? null;
      warmNextPracticeQueue(mode);
      return;
    }

    await loadPracticeQueue(mode);
  }

  function goToMenu() {
    goToDashboard();
    replaceHash("dashboard");
    resetPracticeSurface();
    scheduleDashboardRefresh(200);
  }

  async function advancePracticeCard() {
    resetAnswer();
    resetAudio();
    if (practiceQueueIndex + 1 < practiceQueueCards.length) {
      practiceQueueIndex += 1;
      currentCard = practiceQueueCards[practiceQueueIndex] ?? null;
      if (practiceQueueCards.length - practiceQueueIndex <= 2) {
        warmNextPracticeQueue(practiceQueueMode ?? "mixed");
      }
      return;
    }

    const mode = practiceQueueMode ?? "mixed";
    const prefetched = prefetchedPracticeQueues.get(mode);
    if (prefetched) {
      prefetchedPracticeQueues.delete(mode);
      applyPracticeQueue(mode, prefetched);
      return;
    }
    await loadPracticeQueue(mode);
  }

  const soundEffectCache = new Map();

  function prepareSoundEffect(src, volume = 1.0) {
    if (!src || typeof Audio === "undefined") return null;
    let cached = soundEffectCache.get(src);
    if (!cached) {
      cached = new Audio(src);
      cached.preload = "auto";
      cached.load();
      soundEffectCache.set(src, cached);
    }
    const effect = cached.cloneNode(true);
    effect.volume = Math.max(0, Math.min(1, Number(volume) || 0));
    return effect;
  }

  function playSoundEffect(src, volume = 1.0) {
    if (!soundEffectsEnabledFromMode($soundEffectsMode)) return;
    try {
      const effect = prepareSoundEffect(src, volume);
      void effect?.play();
    } catch (_) {
      // Non-blocking UX hint only.
    }
  }

  function preloadPracticeSoundEffects() {
    if (!soundEffectsEnabledFromMode($soundEffectsMode)) return;
    prepareSoundEffect("/assets/sound_effects/correct_answer.wav", 1.0);
    prepareSoundEffect("/assets/sound_effects/incorrect_answer.wav", 0.6);
    prepareSoundEffect("/assets/sound_effects/show_answer.wav", 0.7);
    prepareSoundEffect("/assets/sound_effects/atchevement.wav", 1.0);
  }

  function playShowAnswerSound() {
    playSoundEffect("/assets/sound_effects/show_answer.wav", 0.7);
  }

  function playFeedbackSound(correct) {
    const src = correct ? "/assets/sound_effects/correct_answer.wav" : "/assets/sound_effects/incorrect_answer.wav";
    playSoundEffect(src, correct ? 1.0 : 0.6);
  }

  function playAchievementSound() {
    playSoundEffect("/assets/sound_effects/atchevement.wav", 1.0);
  }

  function latestAchievement(payload) {
    const achievements = Array.isArray(payload?.achievements) ? payload.achievements : [];
    return [...achievements].sort((a, b) => Number(b?.threshold ?? 0) - Number(a?.threshold ?? 0))[0] ?? null;
  }

  function dismissAchievement() {
    activeAchievement = null;
  }

  function scheduleDashboardRefresh(delay = 400) {
    if (dashboardRefreshTimer) clearTimeout(dashboardRefreshTimer);
    dashboardRefreshTimer = setTimeout(() => {
      dashboardRefreshSignal += 1;
      dashboardRefreshTimer = null;
    }, delay);
  }

  async function recordAnswer(body, submissionCardId, options = {}) {
    if (!options.optimistic) {
      answerSubmitting = true;
    }
    answerErr = "";
    practiceErr = "";

    try {
      const { response, payload } = await submitPracticeAnswer(body);
      // Discard response if user already moved to a different card.
      if (submissionCardId !== currentCard?.id) return;
      if (!response.ok || payload.ok === false) {
        practiceErr = payload?.detail ?? "Could not record answer.";
        return;
      }
      answerResult = payload;
      const achievement = latestAchievement(payload);
      if (achievement) {
        activeAchievement = achievement;
        void playAchievementSound();
      }
      miradAudioUnlocked = true;
      scheduleDashboardRefresh();
      if (options.playSfx !== false) {
        void playFeedbackSound(Boolean(payload?.correct));
      }
      warmNextPracticeQueue(practiceQueueMode ?? "mixed");
    } catch (_) {
      practiceErr = "Could not record answer.";
    } finally {
      answerSubmitting = false;
    }
  }

  async function submitAnswer(event) {
    const answer = event.detail.answer?.trim?.() ?? typedAnswer.trim();
    typedAnswer = answer;
    if (!currentCard?.id || !answer) {
      answerErr = "Enter an answer before submitting.";
      return;
    }
    answerSubmitting = true;
    const submittedCardId = currentCard.id;
    currentSubmissionCardId = submittedCardId;
    void recordAnswer({ card_id: currentCard.id, answer }, submittedCardId, { playSfx: true });
  }

  async function submitGiveUp() {
    if (!currentCard?.id) return;
    answerErr = "";
    playShowAnswerSound();
    answerResult = optimisticAnswerResult(currentCard, "", false);
    miradAudioUnlocked = true;
    const submittedCardId = currentCard.id;
    currentSubmissionCardId = submittedCardId;
    void recordAnswer({ card_id: currentCard.id, correct: false }, submittedCardId, { playSfx: false, optimistic: true });
  }

  let preloadedAudio = $state(/** @type {{ blobUrl: string; audio: HTMLAudioElement } | null} */ (null));
  let preloadedCardId = $state(/** @type {string | null} */ (null));

  function preloadCardAudio() {
    if (!currentCard) return;
    const cardId = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;
    if (!cardId || cardId === preloadedCardId) return;
    preloadedCardId = cardId;
    preloadedAudio = null;
    void (async () => {
      try {
        const response = await fetch(getPracticeAudioUrl(cardId), { headers: { Accept: "audio/wav,application/json" } });
        const contentType = response.headers.get("content-type") ?? "";
        if (!response.ok || !contentType.includes("audio")) return;
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.playbackRate = Number.isFinite(Number($ttsSpeed)) ? Number($ttsSpeed) : 0.8;
        preloadedAudio = { blobUrl: url, audio };
      } catch (_) {
        // Prefetch failure is non-fatal; playCardAudio will retry.
      }
    })();
  }

  async function playCardAudio() {
    if (!currentCard) return;
    resetAudio();
    audioState = "loading";

    try {
      const cardId = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;

      // Use preloaded audio if available for the current card.
      if (preloadedAudio && preloadedCardId === cardId) {
        const { blobUrl, audio } = preloadedAudio;
        audioBlobUrl = blobUrl;
        activeAudio = audio;
        preloadedAudio = null;
        await audio.play();
        audioState = "ready";
        audioMsg = "";
        return;
      }

      const response = await fetch(getPracticeAudioUrl(cardId), { headers: { Accept: "audio/wav,application/json" } });
      const contentType = response.headers.get("content-type") ?? "";

      if (!response.ok || !contentType.includes("audio")) {
        const payload = await readJson(response);
        audioState = response.status === 404 ? "unavailable" : "error";
        audioMsg = payload?.detail ?? "Audio unavailable.";
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioBlobUrl = url;
      activeAudio = audio;
      audio.playbackRate = Number.isFinite(Number($ttsSpeed)) ? Number($ttsSpeed) : 0.8;
      await audio.play();
      audioState = "ready";
      audioMsg = "";
    } catch (_) {
      audioState = "error";
      audioMsg = "Could not play audio.";
    }
  }

  function canPlayAudio() {
    if (!currentCard) return false;
    return currentCard.prompt_language !== "english" || miradAudioUnlocked;
  }

  async function handleLookup(event) {
    const { word, language, anchorRect } = event.detail;
    const direction = language === 'mirad' ? 'mir_to_en' : 'en_to_mir';
    bubbleResults = [];
    bubbleVisible = true;
    bubbleAnchorRect = anchorRect;
    bubbleDirection = direction;
    bubbleLoading = true;
    bubbleError = '';

    try {
      const exact = await lookupExact(word, direction);
      if (exact.length > 0) {
        bubbleResults = exact;
      } else {
        const semantic = await lookupWord(word, direction, 3);
        bubbleResults = semantic;
      }
    } catch (err) {
      bubbleError = err instanceof Error ? err.message : 'Lookup failed';
    } finally {
      bubbleLoading = false;
    }
  }


  async function submitDeleteAccount() {
    if (!canSubmitDelete()) return;

    deleteAccountState = "submitting";
    deleteAccountErr = "";
    deleteAccountStatus = "";

    try {
      const { response, payload } = await deleteAccount(deleteAccountEmail, deleteAccountConfirm);
      if (!response.ok || payload.ok === false) {
        deleteAccountState = "error";
        deleteAccountErr = payload?.detail ?? "Could not delete account.";
        return;
      }
      deleteAccountStatus = `Deleted ${payload?.deleted_email ?? deleteAccountEmail}.`;
      clearAuthAppState("Account deleted.");
    } catch (_) {
      deleteAccountState = "error";
      deleteAccountErr = "Could not delete account.";
    }
  }

  const canDeleteAccount = () => ($currentUser?.role ?? "") !== "admin";
  const deleteConfirmPhrase = () => `${$currentUser?.email ?? ""} DELETE`.trim();
  const canSubmitDelete = () => (
    deleteAccountEmail.trim() === ($currentUser?.email ?? "") && deleteAccountConfirm.trim() === deleteConfirmPhrase()
  );

  async function navigateToSection(section) {
    if ($authState !== "authenticated") return;

    if (section === "dashboard") {
      goToDashboard();
      replaceHash("dashboard");
      resetPracticeSurface();
      scheduleDashboardRefresh(200);
      return;
    }

    if (section === "practice") {
      await openPracticeMode("mixed");
      return;
    }

    if (section === "revision") {
      await openPracticeMode("revision");
      return;
    }

    if (section === "build_vocabulary") {
      await openPracticeMode("build_vocabulary");
      return;
    }

    if (section === "admin" && !isAdminUser($currentUser)) {
      goToDashboard();
      replaceHash("dashboard");
      return;
    }

    resetAudio();
    resetAnswer();
    setCurrentSection(section);
    replaceHash(section);

    if (section === "settings") {
      deleteAccountEmail = $currentUser?.email ?? deleteAccountEmail;
      await loadSettings();
    }
  }

  function scrollWelcomeTarget(id) {
    if (typeof document === "undefined") return;
    const node = document.getElementById(id);
    if (!node) return;
    node.scrollIntoView({ behavior: "smooth", block: "start" });
    // Fallback: scroll by px if element is off-screen
    requestAnimationFrame(() => {
      const el = document.getElementById(id);
      if (!el) return;
      const rect = el.getBoundingClientRect();
      if (rect.top < 0 || rect.bottom > window.innerHeight) {
        el.scrollIntoView({ block: "center" });
      }
    });
  }

  function syncRouteFromHash(fallback = "dashboard") {
    if (typeof window === "undefined" || $authState !== "authenticated") return;
    const hash = window.location.hash.replace(/^#/, "");
    const target = hash || fallback;

    if (target === "practice") {
      void navigateToSection("practice");
      return;
    }
    if (target === "analytics") {
      void navigateToSection("analytics");
      return;
    }
    if (target === "settings") {
      void navigateToSection("settings");
      return;
    }
    if (target === "lexicon") {
      void navigateToSection("lexicon");
      return;
    }
    if (target === "admin") {
      void navigateToSection("admin");
      return;
    }

    void navigateToSection("dashboard");
  }

  $effect(() => {
    if (currentCard?.id !== activeCardId) {
      activeCardId = currentCard?.id ?? null;
      currentSubmissionCardId = null;
      resetAnswer();
    }
  });

  $effect(() => {
    const audioCardId = currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null;
    if (audioCardId !== lastAudioCardId) {
      resetAudio();
      lastAudioCardId = audioCardId;
    }
  });

  // Prefetch audio immediately when an answer is revealed, so it loads in parallel
  // with the visual reveal animation. The play is triggered after a short delay.
  $effect(() => {
    if (!answerResult || !currentCard) {
      preloadedCardId = null;
      preloadedAudio = null;
      return;
    }
    preloadCardAudio();
  });

  $effect(() => {
    const revealCardId = answerResult && currentCard ? (currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id) : null;
    if (!revealCardId || !ttsAutoplayEnabled || !canPlayAudio()) return;
    if (revealCardId === lastAutoplayRevealCardId) return;

    lastAutoplayRevealCardId = revealCardId;
    void (async () => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const currentRevealCardId = currentCard ? (currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id) : null;
      if (currentRevealCardId !== revealCardId) return;
      await playCardAudio();
    })();
  });

  $effect(() => {
    applyTheme($theme);
  });

  $effect(() => {
    if (soundEffectsEnabledFromMode($soundEffectsMode)) preloadPracticeSoundEffects();
  });

  onMount(() => {
    const media = typeof window !== "undefined" && window.matchMedia
      ? window.matchMedia("(prefers-color-scheme: dark)")
      : null;
    const handleSystemThemeChange = () => {
      if ($theme === "system") applyTheme("system");
    };

    media?.addEventListener?.("change", handleSystemThemeChange);
    resetToken = readResetTokenFromUrl();
    void loadCurrentUser();

    return () => {
      media?.removeEventListener?.("change", handleSystemThemeChange);
    };
  });
</script>

<svelte:head>
  <title>MiraLingo</title>
  <meta name="description" content="Practice Mirad." />
</svelte:head>

<svelte:window on:hashchange={() => syncRouteFromHash()} />

{#if resetToken}
  <ResetPassword
    bind:newPassword={resetNewPassword}
    bind:confirmPassword={resetConfirmPassword}
    submitting={resetSubmitting}
    error={resetError}
    message={resetMessage}
    on:submit={submitPasswordReset}
    on:cancel={cancelPasswordReset}
  />
{:else if $authState === "authenticated" && practiceSection($currentSection)}
  <StudyShell
    title={practiceTitle($currentSection)}
    subtitle=""
    userLabel=""
    avatarLabel={displayName($currentUser)}
    showAdmin={isAdminUser($currentUser)}
    backLabel="Back to today"
    on:click={goToMenu}
    on:settings={() => navigateToSection("settings")}
    on:admin={() => navigateToSection("admin")}
    on:analytics={() => navigateToSection("analytics")}
    on:logout={logout}
  >
    <svelte:fragment slot="status">
      {#if practiceState === "loading"}
        <p class="mb-4 text-center text-sm text-slate-500 dark:text-slate-400">Loading practice queue…</p>
      {:else if practiceState === "empty"}
        <p class="mb-4 text-center text-sm text-slate-500 dark:text-slate-400">{practiceErr}</p>
      {:else if practiceState === "error"}
        <p class="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300" role="alert">{practiceErr}</p>
      {/if}
    </svelte:fragment>

    {#if practiceState === "empty"}
      <AppCard className="mx-auto w-full max-w-sm space-y-4 rounded-[2rem] p-6 text-center shadow-lg sm:max-w-md">
        <div class="space-y-2">
          <p class="text-lg font-semibold text-slate-900 dark:text-slate-50">{practiceTitle($currentSection)} is clear</p>
          <p class="text-sm text-slate-500 dark:text-slate-400">{practiceErr}</p>
        </div>
        <div class="grid gap-3">
          {#if $currentSection !== "practice"}
            <AppButton className="min-h-12 w-full justify-center" on:click={() => navigateToSection("practice")}>Go to Practice</AppButton>
          {/if}
          {#if $currentSection !== "build_vocabulary"}
            <AppButton variant="secondary" className="min-h-12 w-full justify-center" on:click={() => navigateToSection("build_vocabulary")}>Build Vocabulary</AppButton>
          {/if}
        </div>
      </AppCard>
    {:else}
      <ExerciseCard
        card={currentCard}
        answer={typedAnswer}
        answerError={answerErr}
        practiceError={practiceErr}
        submitting={answerSubmitting}
        {answerResult}
        audioLoading={audioState === "loading"}
        audioMessage={audioState === "error" || audioState === "unavailable" ? audioMsg : ""}
        audioEnabled={canPlayAudio()}
        on:submit={submitAnswer}
        on:reveal={submitGiveUp}
        on:continue={advancePracticeCard}
        on:audio={playCardAudio}
        on:lookup={handleLookup}
      />
      {#if activeAchievement}
        <div class="fixed inset-x-4 bottom-6 z-50 mx-auto max-w-md rounded-[2rem] border border-amber-200 bg-white/95 p-5 text-left shadow-2xl shadow-amber-500/20 backdrop-blur dark:border-amber-500/40 dark:bg-slate-950/95" role="status" aria-live="polite" data-testid="achievement-toast">
          <div class="flex items-start gap-4">
            <div class="flex h-12 w-12 flex-none items-center justify-center rounded-2xl bg-amber-100 text-2xl dark:bg-amber-400/20" aria-hidden="true">🏆</div>
            <div class="min-w-0 flex-1 space-y-1">
              <p class="text-sm font-semibold uppercase tracking-[0.2em] text-amber-600 dark:text-amber-300">Achievement unlocked</p>
              <h2 class="text-lg font-bold text-slate-950 dark:text-slate-50">{activeAchievement.title ?? "Achievement unlocked!"}</h2>
              <p class="whitespace-pre-line text-sm leading-6 text-slate-600 dark:text-slate-300">{activeAchievement.message ?? "Keep up the good work!"}</p>
            </div>
            <button class="rounded-full px-3 py-1 text-sm font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-500 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white" type="button" aria-label="Dismiss achievement" onclick={dismissAchievement}>×</button>
          </div>
        </div>
      {/if}
    {/if}
  </StudyShell>
{:else if $authState === "authenticated" && $currentSection === "dashboard"}
  <Dashboard
    userName={displayName($currentUser)}
    activeSection={$currentSection}
    refreshSignal={dashboardRefreshSignal}
    showAdmin={isAdminUser($currentUser)}
    on:continuePractice={() => navigateToSection("practice")}
    on:revision={() => navigateToSection("revision")}
    on:buildVocabulary={() => navigateToSection("build_vocabulary")}
    on:lexicon={() => navigateToSection("lexicon")}
    on:settings={() => navigateToSection("settings")}
    on:analytics={() => navigateToSection("analytics")}
    on:admin={() => navigateToSection("admin")}
    on:logout={logout}
  />
{:else if $authState === "authenticated" && $currentSection === "analytics"}
  <Analytics
    userName={displayName($currentUser)}
    activeSection={$currentSection}
    navItems={navItemsFor($currentSection)}
    showAdmin={isAdminUser($currentUser)}
    onBack={goToMenu}
    onSettings={() => navigateToSection("settings")}
    onAdmin={() => navigateToSection("admin")}
    onLogout={logout}
  />
{:else if $authState === "authenticated" && $currentSection === "settings"}
  <AppShell
    title="Settings"
    subtitle="Personalize theme and speech speed"
    showBackButton={true}
    backLabel="Back to today"
    userLabel="Settings"
    avatarLabel={displayName($currentUser)}
    navItems={navItemsFor($currentSection)}
    showAdmin={isAdminUser($currentUser)}
    on:click={goToMenu}
    on:settings={() => navigateToSection("settings")}
    on:admin={() => navigateToSection("admin")}
    on:analytics={() => navigateToSection("analytics")}
    on:logout={logout}
  >
    <div class="space-y-4">
      {#if settingsErr}
        <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"><p role="alert">{settingsErr}</p></AppCard>
      {/if}
      {#if deleteAccountErr}
        <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"><p role="alert">{deleteAccountErr}</p></AppCard>
      {/if}
      {#if deleteAccountStatus}
        <AppCard className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"><p>{deleteAccountStatus}</p></AppCard>
      {/if}

      <AppCard>
        <div class="space-y-6">
          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">Theme</legend>
            <div class="inline-flex rounded-2xl border border-violet-100 bg-slate-50 p-1 dark:border-violet-900/60 dark:bg-slate-900/70">
              {#each [{ v: "system", l: "System" }, { v: "light", l: "Light" }, { v: "dark", l: "Dark" }] as option (option.v)}
                {@const isSelected = $theme === option.v}
                <label class="flex flex-1 cursor-pointer justify-center">
                  <input class="sr-only" type="radio" value={option.v} bind:group={$theme} onchange={() => saveSettings()} />
                  <!-- pointer-events-none lets clicks fall through to the hidden radio input -->
                  <span class="pointer-events-none flex flex-col rounded-xl px-6 py-3 text-left text-sm transition-all duration-200 {isSelected ? 'bg-violet-600 text-white shadow-sm dark:bg-violet-400 dark:text-slate-950' : 'text-slate-600 hover:bg-violet-50 hover:text-violet-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-violet-200'}">
                    <span class="font-semibold">{option.l}</span>
                  </span>
                </label>
              {/each}
            </div>
          </fieldset>

          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">TTS speed</legend>
            <div class="flex flex-col gap-3">
              <input class="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-violet-600 dark:bg-slate-700 dark:accent-violet-400" max="1.2" min="0.5" step="0.1" type="range" bind:value={$ttsSpeed} onchange={() => saveSettings()} />
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-500 dark:text-slate-400">Slow (0.5×)</span>
                <span class="font-semibold text-violet-600 dark:text-violet-400">{spd($ttsSpeed)}</span>
                <span class="text-slate-500 dark:text-slate-400">Fast (1.2×)</span>
              </div>
            </div>
          </fieldset>

          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">Autoplay Mirad audio</legend>
            <label class="flex cursor-pointer items-center justify-between gap-3 rounded-2xl border border-violet-100 px-4 py-3 text-sm font-medium dark:border-violet-900/60">
              <span>Play Mirad TTS automatically after revealing the answer</span>
              <span class="relative inline-flex h-7 w-14 items-center rounded-full bg-slate-300 p-1 shadow-inner transition-colors duration-200 dark:bg-slate-700 {ttsAutoplayEnabled ? 'bg-violet-600 dark:bg-violet-500' : 'bg-slate-300 dark:bg-slate-700'}" aria-hidden="true">
                <span class="absolute left-2 text-[10px] font-bold uppercase text-white/90 opacity-0 transition-opacity {ttsAutoplayEnabled ? 'opacity-100' : ''}">On</span>
                <span class="absolute right-1.5 text-[10px] font-bold uppercase text-slate-600 transition-opacity dark:text-slate-200 {ttsAutoplayEnabled ? 'opacity-0' : 'opacity-100'}">Off</span>
                <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform duration-200 dark:bg-slate-950 {ttsAutoplayEnabled ? 'translate-x-7' : 'translate-x-0'}"></span>
              </span>
              <input type="checkbox" class="sr-only" bind:checked={ttsAutoplayEnabled} onchange={() => saveSettings()} />
            </label>
          </fieldset>

          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">Sound settings</legend>
            <div class="space-y-3">
              <label class="flex cursor-pointer items-center justify-between gap-3 rounded-2xl border border-violet-100 px-4 py-3 text-sm font-medium dark:border-violet-900/60">
                <span>Button Sounds</span>
                <span class="relative inline-flex h-7 w-14 items-center rounded-full bg-slate-300 p-1 shadow-inner transition-colors duration-200 dark:bg-slate-700 {uiButtonSoundsEnabledFromMode($soundEffectsMode) ? 'bg-violet-600 dark:bg-violet-500' : 'bg-slate-300 dark:bg-slate-700'}" aria-hidden="true">
                  <span class="absolute left-2 text-[10px] font-bold uppercase text-white/90 opacity-0 transition-opacity {uiButtonSoundsEnabledFromMode($soundEffectsMode) ? 'opacity-100' : ''}">On</span>
                  <span class="absolute right-1.5 text-[10px] font-bold uppercase text-slate-600 transition-opacity dark:text-slate-200 {uiButtonSoundsEnabledFromMode($soundEffectsMode) ? 'opacity-0' : 'opacity-100'}">Off</span>
                  <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform duration-200 dark:bg-slate-950 {uiButtonSoundsEnabledFromMode($soundEffectsMode) ? 'translate-x-7' : 'translate-x-0'}"></span>
                </span>
                <input type="checkbox" class="sr-only" checked={uiButtonSoundsEnabledFromMode($soundEffectsMode)} onchange={(event) => setUiButtonSounds(event.currentTarget.checked)} />
              </label>

              <div class="flex items-center justify-between gap-3 rounded-2xl border border-violet-100 px-4 py-3 text-sm font-medium dark:border-violet-900/60">
                <span class="flex items-center gap-2">
                  <span>Practice Effects</span>
                  <button
                    type="button"
                    class="relative inline-flex h-6 w-6 items-center justify-center rounded-full text-slate-500 transition hover:bg-violet-50 hover:text-violet-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-violet-200"
                    aria-label="Sound effects information"
                    aria-expanded={soundEffectsInfoOpen}
                    onmouseenter={() => (soundEffectsInfoOpen = true)}
                    onmouseleave={() => (soundEffectsInfoOpen = false)}
                    onclick={(event) => { event.preventDefault(); soundEffectsInfoOpen = !soundEffectsInfoOpen; }}
                  >
                    <span aria-hidden="true">👁</span>
                    {#if soundEffectsInfoOpen}
                      <span class="absolute left-1/2 top-8 z-20 w-64 -translate-x-1/2 rounded-2xl border border-violet-100 bg-white p-3 text-left text-xs font-normal leading-5 text-slate-600 shadow-xl shadow-slate-950/10 dark:border-violet-900/60 dark:bg-slate-950 dark:text-slate-300">
                        Practice Effects play for correct answers, incorrect answers, reveal answer, and achievement celebrations.
                      </span>
                    {/if}
                  </button>
                </span>
                <label class="relative inline-flex cursor-pointer items-center">
                  <span class="relative inline-flex h-7 w-14 items-center rounded-full bg-slate-300 p-1 shadow-inner transition-colors duration-200 dark:bg-slate-700 {soundEffectsEnabledFromMode($soundEffectsMode) ? 'bg-violet-600 dark:bg-violet-500' : 'bg-slate-300 dark:bg-slate-700'}" aria-hidden="true">
                    <span class="absolute left-2 text-[10px] font-bold uppercase text-white/90 opacity-0 transition-opacity {soundEffectsEnabledFromMode($soundEffectsMode) ? 'opacity-100' : ''}">On</span>
                    <span class="absolute right-1.5 text-[10px] font-bold uppercase text-slate-600 transition-opacity dark:text-slate-200 {soundEffectsEnabledFromMode($soundEffectsMode) ? 'opacity-0' : 'opacity-100'}">Off</span>
                    <span class="inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform duration-200 dark:bg-slate-950 {soundEffectsEnabledFromMode($soundEffectsMode) ? 'translate-x-7' : 'translate-x-0'}"></span>
                  </span>
                  <input type="checkbox" class="sr-only" checked={soundEffectsEnabledFromMode($soundEffectsMode)} onchange={(event) => setPracticeSoundEffects(event.currentTarget.checked)} />
                </label>
              </div>
            </div>
          </fieldset>
        </div>
      </AppCard>
    </div>

    <svelte:fragment slot="sidebar">
      <AppCard className="space-y-4">
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Danger zone</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Account deletion still uses the existing auth endpoint and confirmation contract.</p>
        </div>

        {#if canDeleteAccount()}
          <form class="space-y-3" onsubmit={(event) => { event.preventDefault(); submitDeleteAccount(); }}>
            <AppInput id="del-email" label="Email" bind:value={deleteAccountEmail} autocomplete="email" />
            <AppInput id="del-confirm" label={`Type ${deleteConfirmPhrase()} to confirm`} bind:value={deleteAccountConfirm} placeholder={deleteConfirmPhrase()} />
            <AppButton type="submit" className="min-h-12 w-full justify-center bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500 disabled:bg-red-300" disabled={!canSubmitDelete() || deleteAccountState === "submitting"}>
              {deleteAccountState === "submitting" ? "Deleting…" : "Delete account"}
            </AppButton>
          </form>
        {:else}
          <p class="text-sm text-slate-500 dark:text-slate-400">Admin account cannot be deleted.</p>
        {/if}
      </AppCard>
    </svelte:fragment>
  </AppShell>
{:else if $authState === "authenticated" && $currentSection === "admin" && isAdminUser($currentUser)}
  <AdminDashboard
    userName={displayName($currentUser)}
    navItems={navItemsFor($currentSection)}
    on:settings={() => navigateToSection("settings")}
    on:logout={logout}
  />
{:else if $authState === "authenticated" && $currentSection === "lexicon"}
  <Lexicon
    userName={displayName($currentUser)}
    navItems={navItemsFor($currentSection)}
    showAdmin={isAdminUser($currentUser)}
    on:back={goToMenu}
    on:settings={() => navigateToSection("settings")}
    on:admin={() => navigateToSection("admin")}
    on:analytics={() => navigateToSection("analytics")}
    on:logout={logout}
  />
{:else}
  <Welcome
    bind:loginEmail={loginEmail}
    bind:loginPassword={password}
    bind:registrationEmail={registrationEmail}
    bind:registrationName={registrationName}
    bind:registrationPassword={regP}
    {submitting}
    authState={$authState}
    authError={$authError}
    authMessage={$authMessage}
    on:createAccount={submitRegistration}
    on:logIn={submitLogin}
    on:googleLogin={() => { window.location.href = '/auth/google/login'; }}
    on:forgotPassword={submitPasswordResetRequest}
    on:jumpCreateAccount={() => scrollWelcomeTarget("create-account-card")}
    on:jumpLogin={() => scrollWelcomeTarget("login-card")}
  />
{/if}

<LexiconBubble
  results={bubbleResults}
  bind:visible={bubbleVisible}
  anchorRect={bubbleAnchorRect}
  direction={bubbleDirection}
  loading={bubbleLoading}
  error={bubbleError}
/>
