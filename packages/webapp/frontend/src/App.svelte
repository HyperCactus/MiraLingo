<script>
  import "./app.css";

  const docsLinks = [
    {
      href: "../../README.md",
      label: "Project roadmap",
      description: "See how MiraLingo fits into the Mirad tools monorepo.",
    },
    {
      href: "../README.md",
      label: "Web app scope",
      description: "Review the planned pronunciation, translation, and vocabulary loops.",
    },
    {
      href: "../../packages/translator/README.md",
      label: "Translator engine",
      description: "Learn about the Mirad translation components behind practice flows.",
    },
  ];

  const menuSections = [
    {
      title: "Continue Practice",
      description: "Resume the mixed queue with typed recall, answer reveal, and local queue diagnostics.",
      actionLabel: "Open mixed queue",
      section: "practice",
      mode: "mixed",
    },
    {
      title: "Revision",
      description: "Focus on stale mastered review items that need another pass.",
      actionLabel: "Open revision queue",
      section: "revision",
      mode: "revision",
    },
    {
      title: "Build Vocabulary",
      description: "Pull new-item-focused cards to expand active Mirad vocabulary.",
      actionLabel: "Open vocabulary queue",
      section: "build_vocabulary",
      mode: "build_vocabulary",
    },
    {
      title: "Analytics",
      description: "Inspect progress percentage, accuracy, and weak cards away from the practice card surface.",
      actionLabel: "Open analytics",
      section: "analytics",
    },
    {
      title: "Settings",
      description: "Review saved theme, 0.8x speech speed, current voice metadata, and confirmed account deletion controls.",
      actionLabel: "Open settings",
      section: "settings",
    },
    {
      title: "Log Out",
      description: "End this browser session and clear practice, answer, audio, analytics, and settings state.",
      actionLabel: "Log Out",
      action: "logout",
    },
  ];

  const DEFAULT_SETTINGS = {
    theme: "system",
    tts_speed: 0.8,
    voice: {
      id: "de6",
      label: "Mirad de6",
      provider: "mbrola",
      mutable: false,
    },
  };

  const SETTINGS_SPEED_OPTIONS = [0.7, 0.8, 0.9, 1.0, 1.1];

  let username = "admin";
  let password = "";
  let registerUsername = "";
  let registerPassword = "";
  let authState = "checking";
  let user = null;
  let errorMessage = "";
  let isSubmitting = false;

  let activeSection = "menu";
  let activePracticeMode = "mixed";

  let practiceState = "idle";
  let practiceError = "";
  let practiceQueue = null;
  let currentCard = null;
  let answerSubmitting = false;
  let typedAnswer = "";
  let answerError = "";
  let answerResult = null;
  let activeCardId = null;

  let audioState = "idle";
  let audioMessage = "";
  let audioDiagnostic = "";
  let audioBlobUrl = "";
  let activeAudio = null;
  let lastAudioCardId = null;

  let analyticsState = "idle";
  let analyticsError = "";
  let analyticsPayload = null;

  let settingsState = "idle";
  let settingsError = "";
  let settingsStatus = "";
  let settingsPhase = "settings_get";
  let settingsLoadedForUser = null;
  let settingsForm = {
    theme: DEFAULT_SETTINGS.theme,
    tts_speed: DEFAULT_SETTINGS.tts_speed,
  };
  let persistedSettings = structuredClone(DEFAULT_SETTINGS);

  let deleteAccountState = "idle";
  let deleteAccountError = "";
  let deleteAccountStatus = "";
  let deleteAccountUsername = "";
  let deleteAccountConfirmation = "";

  const resetAudioState = () => {
    if (activeAudio) {
      activeAudio.pause();
      activeAudio = null;
    }
    if (audioBlobUrl) {
      URL.revokeObjectURL(audioBlobUrl);
      audioBlobUrl = "";
    }
    audioState = "idle";
    audioMessage = "";
    audioDiagnostic = "";
  };

  const resetAnswerState = () => {
    typedAnswer = "";
    answerError = "";
    answerResult = null;
  };

  const resetPracticeSurface = () => {
    resetAudioState();
    resetAnswerState();
    practiceState = "idle";
    practiceError = "";
    practiceQueue = null;
    currentCard = null;
    activeCardId = null;
    lastAudioCardId = null;
  };

  const resetAnalyticsSurface = () => {
    analyticsState = "idle";
    analyticsError = "";
    analyticsPayload = null;
  };

  const resetSettingsSurface = () => {
    settingsState = "idle";
    settingsError = "";
    settingsStatus = "";
    settingsPhase = "settings_get";
    settingsLoadedForUser = null;
    settingsForm = {
      theme: DEFAULT_SETTINGS.theme,
      tts_speed: DEFAULT_SETTINGS.tts_speed,
    };
    persistedSettings = structuredClone(DEFAULT_SETTINGS);
    deleteAccountState = "idle";
    deleteAccountError = "";
    deleteAccountStatus = "";
    deleteAccountUsername = "";
    deleteAccountConfirmation = "";
  };

  const friendlyAudioError = (payload, status) => {
    if (status === 401 || payload?.error === "unauthenticated") {
      return "Your session expired. Log in again to hear this card.";
    }
    if (payload?.detail) return payload.detail;
    if (payload?.error === "mbrola_unavailable") return "Mirad audio is unavailable on this server.";
    if (payload?.error === "mbrola_voice_unavailable") return "The Mirad de6 voice is not installed on this server.";
    if (payload?.error === "unknown_card") return "That practice card is no longer available. Refresh the queue.";
    return "Audio is unavailable for this card right now.";
  };

  const formatAudioDiagnostic = (payload) => {
    const detail = payload?.diagnostic ?? payload?.detail ?? payload?.error;
    const backend = payload?.backend ? `backend=${payload.backend}` : "backend=unknown";
    return detail ? `${backend}: ${detail}` : backend;
  };

  const friendlyAuthError = (payload, fallback) => {
    if (payload?.detail) return payload.detail;
    if (payload?.error === "invalid_credentials") return "Invalid username or password.";
    if (payload?.error === "local_admin_disabled") {
      return "Local admin login is only available when development bootstrap is enabled.";
    }
    return fallback;
  };

  const friendlyPracticeError = (payload, fallback) => {
    if (payload?.detail) return payload.detail;
    if (payload?.error === "unauthenticated") return "Your session expired. Log in again to continue practice.";
    if (payload?.error === "unknown_card") return "That practice card is no longer available. Refresh the queue.";
    if (payload?.error === "source_missing") return "Practice content is not configured yet. Check the phrase CSV path.";
    return fallback;
  };

  const friendlyAnalyticsError = (payload, fallback) => {
    if (payload?.detail) return payload.detail;
    if (payload?.error === "unauthenticated") return "Your session expired. Log in again to inspect analytics.";
    if (payload?.error === "source_missing") return "Analytics is unavailable until phrase or word content is configured.";
    return fallback;
  };

  const friendlySettingsError = (payload, fallback) => {
    if (payload?.error === "unauthenticated") return "Your session expired. Log in again to manage settings.";
    if (payload?.detail) return payload.detail;
    return fallback;
  };

  const friendlyDeleteAccountError = (payload, fallback) => {
    if (payload?.error === "unauthenticated") return "Your session expired. Log in again before deleting this account.";
    if (payload?.error === "protected_account") return "The local admin account cannot be deleted from Settings.";
    if (payload?.error === "invalid_confirmation") {
      return "Type your current username and the word DELETE before deleting this account.";
    }
    if (payload?.detail) return payload.detail;
    return fallback;
  };

  const languageLabel = (language) => {
    const normalized = String(language ?? "").trim().toLowerCase();
    if (normalized === "mirad") return "Mirad";
    if (normalized === "english") return "English";
    return "practice";
  };

  const directionLabel = (card) => {
    const prompt = languageLabel(card?.prompt_language);
    const answer = languageLabel(card?.answer_language);
    if (prompt === "practice" || answer === "practice") return card?.direction ?? "practice direction";
    return `${prompt} to ${answer}`;
  };

  const promptLabel = (card) => `${languageLabel(card?.prompt_language)} prompt`;
  const answerLabel = (card) => `${languageLabel(card?.answer_language)} answer`;
  const answerInputLabel = (card) => `Type the ${languageLabel(card?.answer_language)} answer`;
  const formatPercent = (value) => (typeof value === "number" ? `${Math.round(value * 100)}%` : "n/a");
  const formatCount = (value) => (typeof value === "number" ? value : "n/a");
  const hasAnalyticsSummary = (payload) =>
    Boolean(
      payload &&
        [
          payload.event_count,
          payload.total,
          payload.correct,
          payload.incorrect,
          payload.weak_count,
          payload.mastered_count,
          payload.stale_count,
          payload.new_count,
          payload.latest_event,
          payload.per_card?.length,
        ].some((value) => value !== undefined && value !== null),
    );
  const practiceTitle = () => {
    if (activeSection === "revision") return "Revision queue";
    if (activeSection === "build_vocabulary") return "Build vocabulary queue";
    return "Practice queue";
  };
  const practiceEyebrow = () => {
    if (activePracticeMode === "revision") return "Revision session";
    if (activePracticeMode === "build_vocabulary") return "Vocabulary builder";
    return "Adaptive session";
  };
  const currentThemeLabel = (theme) => {
    if (theme === "light") return "Light";
    if (theme === "dark") return "Dark";
    return "System";
  };
  const speedLabel = (speed) => `${Number(speed).toFixed(1)}x`;
  const settingsStatusClass = (state) => (state === "error" ? "error-message" : "status-message");
  const settingsStatusRole = (state) => (state === "error" ? "alert" : "status");
  const canDeleteCurrentAccount = () => (user?.username ?? "") !== "admin";

  function resolvedTheme(theme) {
    if (theme === "dark") return "dark";
    if (theme === "light") return "light";
    if (typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
      return "dark";
    }
    return "light";
  }

  function applyTheme(theme) {
    if (typeof document === "undefined") return;
    const normalizedTheme = ["light", "dark", "system"].includes(theme) ? theme : DEFAULT_SETTINGS.theme;
    const nextResolvedTheme = resolvedTheme(normalizedTheme);
    document.documentElement.dataset.themePreference = normalizedTheme;
    document.documentElement.dataset.theme = nextResolvedTheme;
    document.documentElement.style.colorScheme = nextResolvedTheme;
    document.body?.setAttribute("data-theme", nextResolvedTheme);
  }

  function coerceTheme(theme) {
    return ["light", "dark", "system"].includes(theme) ? theme : DEFAULT_SETTINGS.theme;
  }

  function coerceSpeed(ttsSpeed) {
    const numeric = Number(ttsSpeed);
    return Number.isFinite(numeric) && numeric > 0 && numeric <= 2 ? Number(numeric.toFixed(1)) : DEFAULT_SETTINGS.tts_speed;
  }

  function coerceVoice(voice) {
    const label = typeof voice?.label === "string" && voice.label.trim() ? voice.label.trim() : DEFAULT_SETTINGS.voice.label;
    const id = typeof voice?.id === "string" && voice.id.trim() ? voice.id.trim() : DEFAULT_SETTINGS.voice.id;
    const provider =
      typeof voice?.provider === "string" && voice.provider.trim()
        ? voice.provider.trim()
        : DEFAULT_SETTINGS.voice.provider;
    return {
      id,
      label,
      provider,
      mutable: false,
    };
  }

  function coerceSettingsPayload(payload) {
    const settings = payload?.settings ?? payload ?? {};
    return {
      theme: coerceTheme(settings?.theme),
      tts_speed: coerceSpeed(settings?.tts_speed),
      voice: coerceVoice(settings?.voice),
    };
  }

  function syncSettingsForm(nextSettings, { statusMessage = "", state = "ready", phase = "settings_get" } = {}) {
    const safeSettings = coerceSettingsPayload(nextSettings);
    persistedSettings = safeSettings;
    settingsForm = {
      theme: safeSettings.theme,
      tts_speed: safeSettings.tts_speed,
    };
    settingsState = state;
    settingsPhase = phase;
    settingsError = "";
    settingsStatus = statusMessage;
  }

  async function readJson(response) {
    try {
      return await response.json();
    } catch (_error) {
      return {};
    }
  }

  function goToMenu() {
    resetAudioState();
    resetAnswerState();
    activeSection = "menu";
  }

  async function loadSettings({ force = false } = {}) {
    if (authState !== "authenticated" || !user?.username) return;
    if (!force && settingsLoadedForUser === user.username && settingsState !== "idle") return;

    settingsState = "loading";
    settingsPhase = "settings_get";
    settingsError = "";
    settingsStatus = "Loading saved settings…";
    try {
      const response = await fetch("/settings", {
        headers: { Accept: "application/json" },
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        settingsLoadedForUser = user.username;
        const safeSettings = coerceSettingsPayload(DEFAULT_SETTINGS);
        persistedSettings = safeSettings;
        settingsForm = {
          theme: safeSettings.theme,
          tts_speed: safeSettings.tts_speed,
        };
        settingsState = "error";
        settingsPhase = payload?.phase ?? "settings_get";
        settingsError = friendlySettingsError(payload, "Could not load saved settings. Safe defaults are shown below.");
        settingsStatus = "";
        return;
      }
      syncSettingsForm(payload, { state: "ready", phase: payload?.phase ?? "settings_get" });
      settingsLoadedForUser = user.username;
    } catch (_error) {
      settingsLoadedForUser = user.username;
      const safeSettings = coerceSettingsPayload(DEFAULT_SETTINGS);
      persistedSettings = safeSettings;
      settingsForm = {
        theme: safeSettings.theme,
        tts_speed: safeSettings.tts_speed,
      };
      settingsState = "error";
      settingsPhase = "settings_get";
      settingsError = "Could not reach saved settings. Safe defaults are shown below.";
      settingsStatus = "";
    }
  }

  async function loadCurrentUser() {
    errorMessage = "";
    try {
      const response = await fetch("/auth/current-user", {
        headers: { Accept: "application/json" },
      });
      const payload = await readJson(response);
      if (response.ok && payload.authenticated) {
        user = payload.user;
        authState = "authenticated";
        activeSection = "menu";
        resetPracticeSurface();
        resetAnalyticsSurface();
        resetSettingsSurface();
        deleteAccountUsername = payload.user?.username ?? "";
        await loadSettings({ force: true });
        return;
      }
      user = null;
      authState = "anonymous";
      resetSettingsSurface();
    } catch (_error) {
      user = null;
      authState = "anonymous";
      resetSettingsSurface();
      errorMessage = "Could not reach MiraLingo auth. Check that the web server is running.";
    }
  }

  async function submitLogin() {
    isSubmitting = true;
    errorMessage = "";
    try {
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
      const payload = await readJson(response);
      if (!response.ok || !payload.authenticated) {
        user = null;
        authState = "login-failed";
        errorMessage = friendlyAuthError(payload, "Login failed. Please try again.");
        return;
      }
      user = payload.user;
      password = "";
      authState = "authenticated";
      activeSection = "menu";
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      deleteAccountUsername = payload.user?.username ?? "";
      await loadSettings({ force: true });
    } catch (_error) {
      user = null;
      authState = "login-failed";
      errorMessage = "Could not reach MiraLingo auth. Check that the web server is running.";
    } finally {
      isSubmitting = false;
    }
  }

  async function submitRegistration() {
    isSubmitting = true;
    errorMessage = "";
    try {
      const response = await fetch("/auth/register", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: registerUsername, password: registerPassword }),
      });
      const payload = await readJson(response);
      if (!response.ok || !payload.authenticated) {
        user = null;
        authState = "registration-failed";
        errorMessage = friendlyAuthError(payload, "Registration failed. Choose another username and try again.");
        return;
      }
      user = payload.user;
      password = "";
      registerPassword = "";
      authState = "authenticated";
      activeSection = "menu";
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      deleteAccountUsername = payload.user?.username ?? "";
      await loadSettings({ force: true });
    } catch (_error) {
      user = null;
      authState = "registration-failed";
      errorMessage = "Could not reach MiraLingo registration. Check that the web server is running.";
    } finally {
      isSubmitting = false;
    }
  }

  async function logout() {
    errorMessage = "";
    try {
      await fetch("/auth/logout", { method: "POST", headers: { Accept: "application/json" } });
    } finally {
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      user = null;
      username = "admin";
      password = "";
      registerUsername = "";
      registerPassword = "";
      authState = "anonymous";
      activeSection = "menu";
      activePracticeMode = "mixed";
    }
  }

  async function loadPracticeQueue(mode = activePracticeMode) {
    resetAudioState();
    resetAnswerState();
    practiceState = "loading";
    practiceError = "";
    try {
      let queueUrl = "/practice/queue?mode=mixed&limit=3";
      if (mode === "revision") queueUrl = "/practice/queue?mode=revision&limit=3";
      if (mode === "build_vocabulary") queueUrl = "/practice/queue?mode=build_vocabulary&limit=3";
      const response = await fetch(queueUrl, { headers: { Accept: "application/json" } });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        practiceQueue = payload;
        currentCard = null;
        activeCardId = null;
        lastAudioCardId = null;
        resetAnswerState();
        practiceState = "error";
        practiceError = friendlyPracticeError(payload, "Practice queue is unavailable. Try again after checking the server.");
        return;
      }
      practiceQueue = payload;
      currentCard = payload.cards?.[0] ?? null;
      practiceState = currentCard ? "ready" : "empty";
    } catch (_error) {
      practiceState = "error";
      practiceQueue = null;
      currentCard = null;
      activeCardId = null;
      lastAudioCardId = null;
      resetAnswerState();
      practiceError = "Could not reach practice APIs. Check that the web server is running.";
    }
  }

  async function openPracticeMode(mode) {
    activePracticeMode = mode;
    activeSection = mode === "revision" ? "revision" : mode === "build_vocabulary" ? "build_vocabulary" : "practice";
    resetAnalyticsSurface();
    resetPracticeSurface();
    await loadPracticeQueue(mode);
  }

  async function loadAnalytics() {
    analyticsState = "loading";
    analyticsError = "";
    try {
      const response = await fetch("/practice/progress", {
        headers: { Accept: "application/json" },
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        analyticsPayload = payload;
        analyticsState = "error";
        analyticsError = friendlyAnalyticsError(payload, "Analytics is unavailable right now.");
        return;
      }
      analyticsPayload = payload;
      analyticsState = "ready";
    } catch (_error) {
      analyticsPayload = null;
      analyticsState = "error";
      analyticsError = "Could not reach progress analytics. Check that the web server is running.";
    }
  }

  async function openAnalytics() {
    activeSection = "analytics";
    resetAudioState();
    resetAnswerState();
    await loadAnalytics();
  }

  async function openSettings() {
    activeSection = "settings";
    resetAudioState();
    resetAnswerState();
    deleteAccountUsername = user?.username ?? deleteAccountUsername;
    await loadSettings();
  }

  async function saveSettings() {
    if (settingsState === "saving") return;

    settingsState = "saving";
    settingsPhase = "settings_update";
    settingsError = "";
    settingsStatus = "Saving your learner settings…";

    const payloadBody = {
      theme: coerceTheme(settingsForm.theme),
      tts_speed: coerceSpeed(settingsForm.tts_speed),
    };

    try {
      const response = await fetch("/settings", {
        method: "PUT",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payloadBody),
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        settingsState = "error";
        settingsPhase = payload?.phase ?? "settings_update";
        settingsError = friendlySettingsError(payload, "Could not save learner settings. Your unsaved selections are still visible.");
        settingsStatus = "";
        return;
      }
      syncSettingsForm(payload, {
        state: "ready",
        phase: payload?.phase ?? "settings_update",
        statusMessage: "Settings saved. Theme and speech speed will persist for this account.",
      });
      settingsLoadedForUser = user?.username ?? settingsLoadedForUser;
    } catch (_error) {
      settingsState = "error";
      settingsPhase = "settings_update";
      settingsError = "Could not save learner settings. Your unsaved selections are still visible.";
      settingsStatus = "";
    }
  }

  async function submitDeleteAccount() {
    if (deleteAccountState === "submitting" || !user?.username) return;

    deleteAccountState = "submitting";
    deleteAccountError = "";
    deleteAccountStatus = "Deleting this learner account…";

    try {
      const response = await fetch("/auth/account", {
        method: "DELETE",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: deleteAccountUsername,
          confirmation: deleteAccountConfirmation,
        }),
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        deleteAccountState = "error";
        deleteAccountError = friendlyDeleteAccountError(payload, "Could not delete this account right now.");
        deleteAccountStatus = "";
        return;
      }
      deleteAccountState = "done";
      deleteAccountStatus = `Deleted account ${payload.deleted_username ?? user.username}.`;
      deleteAccountError = "";
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      user = null;
      password = "";
      registerPassword = "";
      authState = "anonymous";
      activeSection = "menu";
      activePracticeMode = "mixed";
    } catch (_error) {
      deleteAccountState = "error";
      deleteAccountError = "Could not reach account deletion. Confirm the server and try again.";
      deleteAccountStatus = "";
    }
  }

  async function recordPracticeAnswer(payloadBody) {
    if (!currentCard || answerSubmitting) return;
    answerSubmitting = true;
    practiceError = "";
    answerError = "";
    try {
      const response = await fetch("/practice/answers", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payloadBody),
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        practiceState = "ready";
        practiceError = friendlyPracticeError(payload, "Answer rejected. Refresh the queue and try again.");
        return;
      }
      answerResult = payload;
    } catch (_error) {
      practiceState = "ready";
      practiceError = "Could not submit the practice answer. Check the server and try again.";
    } finally {
      answerSubmitting = false;
    }
  }

  async function submitTypedPracticeAnswer() {
    const normalizedAnswer = typedAnswer.trim();
    answerError = "";
    practiceError = "";
    if (!normalizedAnswer) {
      answerError = `Type a ${languageLabel(currentCard?.answer_language)} answer before submitting.`;
      return;
    }
    await recordPracticeAnswer({ card_id: currentCard.id, answer: normalizedAnswer });
  }

  async function submitGiveUp() {
    answerError = "";
    practiceError = "";
    await recordPracticeAnswer({ card_id: currentCard.id, correct: false });
  }

  async function advancePracticeCard() {
    if (practiceState === "loading" || answerSubmitting) return;
    await loadPracticeQueue();
  }

  async function playCardAudio() {
    if (!currentCard || audioState === "loading") return;
    audioState = "loading";
    audioMessage = "Preparing Mirad audio…";
    audioDiagnostic = "";
    try {
      const audioCardId = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;
      const response = await fetch(`/practice/audio/${encodeURIComponent(audioCardId)}`, {
        headers: { Accept: "audio/wav, application/json" },
      });
      const contentType = response.headers.get("content-type") ?? "";
      if (!response.ok || contentType.includes("application/json")) {
        const payload = await readJson(response);
        audioState = response.status === 401 ? "error" : "unavailable";
        audioMessage = friendlyAudioError(payload, response.status);
        audioDiagnostic = formatAudioDiagnostic(payload);
        return;
      }

      const blob = await response.blob();
      if (audioBlobUrl) URL.revokeObjectURL(audioBlobUrl);
      const nextBlobUrl = URL.createObjectURL(blob);
      audioBlobUrl = nextBlobUrl;
      activeAudio = new Audio(nextBlobUrl);
      activeAudio.playbackRate = coerceSpeed(settingsForm.tts_speed);
      activeAudio.addEventListener("ended", () => {
        audioState = "idle";
        audioMessage = `Audio finished at ${speedLabel(settingsForm.tts_speed)}.`;
      });
      await activeAudio.play();
      audioState = "playing";
      audioMessage = `Playing Mirad audio at ${speedLabel(settingsForm.tts_speed)}.`;
    } catch (_error) {
      audioState = "error";
      audioMessage = "Could not play audio. Check the server, then try again.";
      audioDiagnostic = "network_or_browser_playback";
    }
  }

  function activateMenuItem(item) {
    if (item.action === "logout") {
      logout();
      return;
    }
    if (item.section === "analytics") {
      openAnalytics();
      return;
    }
    if (item.section === "settings") {
      openSettings();
      return;
    }
    if (item.mode) {
      openPracticeMode(item.mode);
    }
  }

  $: if (currentCard?.id !== activeCardId) {
    activeCardId = currentCard?.id ?? null;
    resetAnswerState();
  }

  $: if ((currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null) !== lastAudioCardId) {
    resetAudioState();
    lastAudioCardId = currentCard?.audio_card_id ?? currentCard?.base_card_id ?? currentCard?.id ?? null;
  }

  $: applyTheme(settingsForm.theme);

  loadCurrentUser();
</script>

<svelte:head>
  <title>MiraLingo | Mirad learning lab</title>
  <meta
    name="description"
    content="MiraLingo is a friendly Mirad learning home for pronunciation, translation, and vocabulary practice."
  />
</svelte:head>

{#if authState === "authenticated"}
  <main class="app-shell" aria-labelledby="home-heading">
    <section class="home-panel">
      <div>
        <p class="eyebrow">MiraLingo app home</p>
        <h1 id="home-heading">Welcome back, {user?.username ?? "admin"}.</h1>
        <p class="lede">
          Choose a focused section from the main menu, keep the practice card uncluttered, and reach
          analytics only when you want progress diagnostics.
        </p>
      </div>
      <dl class="status-grid" aria-label="Current session">
        <div>
          <dt>Session</dt>
          <dd>Logged in</dd>
        </div>
        <div>
          <dt>Role</dt>
          <dd>{user?.role ?? "admin"}</dd>
        </div>
        <div>
          <dt>Section</dt>
          <dd>{activeSection}</dd>
        </div>
      </dl>

      {#if activeSection === "menu"}
        <section class="main-menu" aria-labelledby="menu-heading">
          <div class="practice-header">
            <div>
              <p class="eyebrow">Authenticated home</p>
              <h2 id="menu-heading">Main menu</h2>
            </div>
            {#if settingsStatus}
              <p class="settings-inline-status status-message" role="status">{settingsStatus}</p>
            {/if}
          </div>
          <div class="menu-grid">
            {#each menuSections as item}
              <article class="menu-card">
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </div>
                <button class={item.action === "logout" ? "secondary-action" : "primary-action"} type="button" on:click={() => activateMenuItem(item)}>
                  {item.actionLabel}
                </button>
              </article>
            {/each}
          </div>
        </section>
      {/if}

      {#if activeSection === "practice" || activeSection === "revision" || activeSection === "build_vocabulary"}
        <section class="practice-panel" aria-labelledby="practice-heading">
          <div class="practice-header">
            <div>
              <p class="eyebrow">{practiceEyebrow()}</p>
              <h2 id="practice-heading">{practiceTitle()}</h2>
            </div>
            <div class="menu-actions">
              <button class="secondary-action" type="button" on:click={goToMenu}>Back to menu</button>
              <button class="secondary-action" type="button" on:click={loadPracticeQueue} disabled={practiceState === "loading" || answerSubmitting}>
                {practiceState === "loading" ? "Loading…" : "Refresh queue"}
              </button>
            </div>
          </div>

          {#if practiceState === "loading"}
            <p class="status-message" role="status">Loading practice queue…</p>
          {:else if practiceState === "empty"}
            <p class="status-message" role="status">No practice cards are available yet. Import phrase or word content first.</p>
          {:else if practiceError}
            <p class="error-message" role="alert">{practiceError}</p>
          {/if}

          {#if currentCard}
            <article class="practice-card" aria-label="Current practice card">
              <div class="card-meta">
                <span>{currentCard.type}</span>
                <span>Direction: {directionLabel(currentCard)}</span>
                <span>Reason: {currentCard.scheduler_reason}</span>
              </div>
              <p class="prompt-label">{promptLabel(currentCard)}</p>
              <p class="prompt-text">{currentCard.prompt}</p>

              <div class="audio-row" aria-label="Mirad answer audio">
                <button
                  class="audio-button"
                  type="button"
                  aria-label="Play Mirad answer audio"
                  disabled={audioState === "loading"}
                  on:click={playCardAudio}
                >
                  <span aria-hidden="true">🔊</span>
                  {audioState === "loading" ? "Preparing audio…" : audioState === "playing" ? "Playing…" : "Hear Mirad answer"}
                </button>
                <p class="audio-speed-note">Audio uses your current {speedLabel(settingsForm.tts_speed)} learner speed preference.</p>
                {#if audioMessage}
                  <p class={audioState === "error" || audioState === "unavailable" ? "error-message" : "status-message"} role={audioState === "error" || audioState === "unavailable" ? "alert" : "status"}>
                    {audioMessage}
                    {#if audioDiagnostic}
                      <span class="audio-diagnostic">{audioDiagnostic}</span>
                    {/if}
                  </p>
                {/if}
              </div>

              <form class="answer-form" aria-label="Typed recall answer form" on:submit|preventDefault={submitTypedPracticeAnswer}>
                <label class="answer-field" for="typed-answer-input">
                  {answerInputLabel(currentCard)}
                </label>
                <input
                  id="typed-answer-input"
                  name="typed-answer"
                  class="answer-input"
                  aria-label="Type your answer"
                  autocomplete="off"
                  bind:value={typedAnswer}
                  disabled={answerSubmitting || answerResult !== null}
                />
                <div class="answer-actions" aria-label="Submit answer">
                  <button class="primary-action" type="submit" disabled={answerSubmitting || answerResult !== null}>
                    {answerSubmitting ? "Submitting…" : "Submit answer"}
                  </button>
                  <button class="secondary-action" type="button" disabled={answerSubmitting || answerResult !== null} on:click={submitGiveUp}>
                    Give up
                  </button>
                </div>
              </form>

              {#if answerError}
                <p class="error-message" role="alert">{answerError}</p>
              {/if}

              {#if answerResult}
                <section class="answer-result-panel" aria-labelledby="answer-result-heading">
                  <div class="answer-result-copy">
                    <p class="eyebrow">Answer result</p>
                    <h3 id="answer-result-heading">{answerResult.correct ? "Correct" : "Not quite"}</h3>
                    <p class={answerResult.correct ? "status-message" : "error-message"} role="status">
                      {answerResult.correct ? "Nice recall — backend marked this correct." : "The correct answer is revealed below."}
                    </p>
                  </div>
                  <dl class="answer-result-grid" aria-label="Answer reveal details">
                    <div>
                      <dt>expected_answer</dt>
                      <dd>{answerResult.expected_answer ?? currentCard.answer}</dd>
                    </div>
                    <div>
                      <dt>submitted_answer</dt>
                      <dd>{answerResult.submitted_answer ?? "Give up"}</dd>
                    </div>
                    <div>
                      <dt>correct</dt>
                      <dd>{answerResult.correct ? "true" : "false"}</dd>
                    </div>
                    <div>
                      <dt>scheduler_reason</dt>
                      <dd>{answerResult.scheduler_reason ?? currentCard.scheduler_reason}</dd>
                    </div>
                    <div>
                      <dt>latest_event</dt>
                      <dd>{answerResult.latest_event ? `${answerResult.latest_event.card_id}: ${answerResult.latest_event.correct ? "correct" : "incorrect"}` : "none"}</dd>
                    </div>
                    <div>
                      <dt>event_count</dt>
                      <dd>{answerResult.event_count ?? practiceQueue?.event_count ?? 0}</dd>
                    </div>
                  </dl>
                  <button class="primary-action" type="button" on:click={advancePracticeCard}>
                    Continue
                  </button>
                </section>
              {/if}

              <dl class="diagnostic-grid" aria-label="Practice diagnostics">
                <div>
                  <dt>direction</dt>
                  <dd>{currentCard.direction}</dd>
                </div>
                <div>
                  <dt>event_count</dt>
                  <dd>{answerResult?.event_count ?? practiceQueue?.event_count ?? 0}</dd>
                </div>
                <div>
                  <dt>scheduler_reason</dt>
                  <dd>{answerResult?.scheduler_reason ?? currentCard.scheduler_reason}</dd>
                </div>
                <div>
                  <dt>phase</dt>
                  <dd>{answerResult?.phase ?? practiceQueue?.phase ?? "practice_queue"}</dd>
                </div>
              </dl>
            </article>
          {/if}
        </section>
      {/if}

      {#if activeSection === "analytics"}
        <section class="analytics-panel" aria-labelledby="analytics-heading">
          <div class="practice-header">
            <div>
              <p class="eyebrow">Progress diagnostics</p>
              <h2 id="analytics-heading">Analytics</h2>
            </div>
            <div class="menu-actions">
              <button class="secondary-action" type="button" on:click={goToMenu}>Back to menu</button>
              <button class="secondary-action" type="button" on:click={loadAnalytics} disabled={analyticsState === "loading"}>
                {analyticsState === "loading" ? "Loading…" : "Refresh analytics"}
              </button>
            </div>
          </div>

          {#if analyticsState === "loading"}
            <p class="status-message" role="status">Analytics status: loading progress diagnostics…</p>
          {:else if analyticsError}
            <p class="error-message" role="alert">Analytics error: {analyticsError}</p>
          {:else if analyticsPayload && hasAnalyticsSummary(analyticsPayload)}
            <p class="status-message" role="status">Progress status: {analyticsPayload.phase ?? analyticsPayload.practice_phase ?? "practice_progress"}</p>
            <dl class="analytics-grid">
              <div>
                <dt>event_count</dt>
                <dd>{formatCount(analyticsPayload.event_count) ?? 0}</dd>
              </div>
              <div>
                <dt>accuracy</dt>
                <dd>{formatPercent(analyticsPayload.accuracy)}</dd>
              </div>
              <div>
                <dt>progress percentage</dt>
                <dd>{analyticsPayload.total ? `${Math.round(((analyticsPayload.correct ?? 0) / analyticsPayload.total) * 100)}%` : "n/a"}</dd>
              </div>
              <div>
                <dt>completion percentage</dt>
                <dd>{analyticsPayload.total ? `${Math.round(((analyticsPayload.event_count ?? 0) / analyticsPayload.total) * 100)}%` : "n/a"}</dd>
              </div>
              <div>
                <dt>weak cards</dt>
                <dd>{formatCount(analyticsPayload.weak_count)}</dd>
              </div>
              <div>
                <dt>mastered cards</dt>
                <dd>{formatCount(analyticsPayload.mastered_count)}</dd>
              </div>
              <div>
                <dt>stale cards</dt>
                <dd>{formatCount(analyticsPayload.stale_count)}</dd>
              </div>
              <div>
                <dt>new cards</dt>
                <dd>{formatCount(analyticsPayload.new_count)}</dd>
              </div>
            </dl>
            <dl class="diagnostic-grid" aria-label="Analytics diagnostics">
              <div>
                <dt>scheduler_reason</dt>
                <dd>{analyticsPayload.latest_event?.scheduler_reason ?? analyticsPayload.per_card?.[0]?.scheduler_reason ?? "none"}</dd>
              </div>
              <div>
                <dt>latest_event</dt>
                <dd>{analyticsPayload.latest_event ? `${analyticsPayload.latest_event.card_id}: ${analyticsPayload.latest_event.correct ? "correct" : "incorrect"}` : "none"}</dd>
              </div>
              <div>
                <dt>word accuracy</dt>
                <dd>{formatPercent(analyticsPayload.per_type?.word?.accuracy)}</dd>
              </div>
              <div>
                <dt>phrase accuracy</dt>
                <dd>{formatPercent(analyticsPayload.per_type?.phrase?.accuracy)}</dd>
              </div>
            </dl>
          {:else}
            <p class="status-message" role="status">
              Analytics status: no progress diagnostics are available yet. Start or refresh practice, then return here.
            </p>
          {/if}
        </section>
      {/if}

      {#if activeSection === "settings"}
        <section class="settings-panel" aria-labelledby="settings-heading">
          <div class="practice-header">
            <div>
              <p class="eyebrow">Learner preferences</p>
              <h2 id="settings-heading">Settings</h2>
            </div>
            <div class="menu-actions">
              <button class="secondary-action" type="button" on:click={goToMenu}>Back to menu</button>
              <button class="secondary-action" type="button" on:click={() => loadSettings({ force: true })} disabled={settingsState === "loading" || settingsState === "saving"}>
                {settingsState === "loading" ? "Loading…" : "Reload settings"}
              </button>
            </div>
          </div>

          {#if settingsStatus}
            <p class={settingsStatusClass(settingsState)} role={settingsStatusRole(settingsState)}>
              Settings status ({settingsPhase}): {settingsStatus}
            </p>
          {/if}
          {#if settingsError}
            <p class="error-message" role="alert">
              Settings error ({settingsPhase}): {settingsError}
            </p>
          {/if}

          <form class="settings-form" aria-label="Learner settings form" on:submit|preventDefault={saveSettings}>
            <section class="settings-card" aria-labelledby="appearance-heading">
              <div>
                <p class="eyebrow">Appearance</p>
                <h3 id="appearance-heading">Theme</h3>
                <p class="settings-copy">
                  Pick how MiraLingo should look for this learner account. System keeps following your device preference.
                </p>
              </div>
              <fieldset class="theme-fieldset">
                <legend>Choose theme</legend>
                <label class="toggle-card">
                  <input bind:group={settingsForm.theme} name="theme" type="radio" value="system" />
                  <span>System</span>
                  <small>Follow device preference</small>
                </label>
                <label class="toggle-card">
                  <input bind:group={settingsForm.theme} name="theme" type="radio" value="light" />
                  <span>Light</span>
                  <small>Bright learner workspace</small>
                </label>
                <label class="toggle-card">
                  <input bind:group={settingsForm.theme} name="theme" type="radio" value="dark" />
                  <span>Dark</span>
                  <small>Lower-glare learner workspace</small>
                </label>
              </fieldset>
              <p class="settings-meta" role="status">Current saved theme: {currentThemeLabel(persistedSettings.theme)}</p>
            </section>

            <section class="settings-card" aria-labelledby="audio-settings-heading">
              <div>
                <p class="eyebrow">Audio</p>
                <h3 id="audio-settings-heading">Speech speed</h3>
                <p class="settings-copy">
                  Choose the default playback speed for Mirad audio. New accounts start at 0.8x to keep speech intelligible.
                </p>
              </div>
              <label class="settings-field" for="tts-speed-select">
                Default TTS speed
              </label>
              <select id="tts-speed-select" bind:value={settingsForm.tts_speed} class="settings-select" name="tts-speed">
                {#each SETTINGS_SPEED_OPTIONS as option}
                  <option value={option}>{speedLabel(option)}</option>
                {/each}
              </select>
              <p class="settings-meta" role="status">
                Current saved speed: {speedLabel(persistedSettings.tts_speed)} · Default for fresh learners: 0.8x
              </p>
            </section>

            <section class="settings-card" aria-labelledby="voice-heading">
              <div>
                <p class="eyebrow">Voice</p>
                <h3 id="voice-heading">Current Mirad voice</h3>
                <p class="settings-copy">
                  MiraLingo currently offers one fixed synthesis voice. It is shown honestly here but cannot be changed yet.
                </p>
              </div>
              <dl class="voice-grid" aria-label="Current voice metadata">
                <div>
                  <dt>Voice label</dt>
                  <dd>{persistedSettings.voice.label}</dd>
                </div>
                <div>
                  <dt>Voice id</dt>
                  <dd>{persistedSettings.voice.id}</dd>
                </div>
                <div>
                  <dt>Provider</dt>
                  <dd>{persistedSettings.voice.provider}</dd>
                </div>
                <div>
                  <dt>Selection</dt>
                  <dd>{persistedSettings.voice.mutable ? "Adjustable" : "Single available voice"}</dd>
                </div>
              </dl>
            </section>

            <div class="settings-actions">
              <button class="primary-action" type="submit" disabled={settingsState === "saving" || settingsState === "loading"}>
                {settingsState === "saving" ? "Saving…" : "Save settings"}
              </button>
            </div>
          </form>

          <section class="settings-card danger-zone" aria-labelledby="danger-zone-heading">
            <div>
              <p class="eyebrow">Danger zone</p>
              <h3 id="danger-zone-heading">Delete current account</h3>
              <p class="settings-copy">
                Delete only the currently signed-in learner account after explicit confirmation. This also removes saved settings and practice history rows for that learner.
              </p>
            </div>

            {#if deleteAccountStatus}
              <p class="status-message" role="status">Account deletion status: {deleteAccountStatus}</p>
            {/if}
            {#if deleteAccountError}
              <p class="error-message" role="alert">Account deletion error: {deleteAccountError}</p>
            {/if}

            {#if canDeleteCurrentAccount()}
              <form class="delete-account-form" aria-label="Delete current account form" on:submit|preventDefault={submitDeleteAccount}>
                <label class="settings-field" for="delete-account-username">Current username</label>
                <input
                  id="delete-account-username"
                  class="settings-input"
                  bind:value={deleteAccountUsername}
                  autocomplete="username"
                  name="delete-account-username"
                />

                <label class="settings-field" for="delete-account-confirmation">Type DELETE to confirm</label>
                <input
                  id="delete-account-confirmation"
                  class="settings-input"
                  bind:value={deleteAccountConfirmation}
                  name="delete-account-confirmation"
                />

                <p class="settings-meta" role="status">
                  You must confirm the current username ({user?.username}) and type DELETE before the account is removed.
                </p>

                <div class="settings-actions">
                  <button class="danger-action" type="submit" disabled={deleteAccountState === "submitting"}>
                    {deleteAccountState === "submitting" ? "Deleting…" : "Delete current account"}
                  </button>
                </div>
              </form>
            {:else}
              <p class="status-message" role="status">
                Account deletion is disabled for the local admin bootstrap user.
              </p>
            {/if}
          </section>
        </section>
      {/if}
    </section>
  </main>
{:else}
  <main class="welcome-shell" aria-labelledby="welcome-heading">
    <section class="hero-card">
      <div class="hero-copy">
        <p class="eyebrow">Mirad learning lab</p>
        <h1 id="welcome-heading">Welcome to MiraLingo</h1>
        <p class="lede">
          Practice Mirad pronunciation, translation, and vocabulary in one warm workspace powered by
          the tools in this repository.
        </p>
        <div class="action-row" aria-label="Primary actions">
          <a class="primary-action" href="#register-panel">Create account</a>
          <a class="secondary-action" href="#login-panel">Log in as local admin</a>
        </div>
        <p class="helper-text">
          Create a learner account for this browser session, or keep using the guarded local admin bootstrap
          when it is enabled by backend settings.
        </p>
      </div>

      <div class="auth-stack" aria-label="MiraLingo authentication options">
        <form id="register-panel" class="login-card" aria-label="Learner registration" on:submit|preventDefault={submitRegistration}>
          <div>
            <p class="eyebrow">Self-service sign up</p>
            <h2>Create learner account</h2>
            <p class="form-note">Registration logs you in immediately for this server session. Passwords are never echoed in errors.</p>
          </div>
          {#if authState === "checking"}
            <p class="status-message" role="status">Checking current session…</p>
          {/if}
          {#if errorMessage && authState === "registration-failed"}
            <p class="error-message" role="alert">{errorMessage}</p>
          {/if}
          <label>
            Username
            <input autocomplete="username" bind:value={registerUsername} name="register-username" required />
          </label>
          <label>
            Password
            <input autocomplete="new-password" bind:value={registerPassword} name="register-password" required type="password" />
          </label>
          <button class="primary-action submit-action" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <form id="login-panel" class="login-card" aria-label="Local admin login" on:submit|preventDefault={submitLogin}>
          <div>
            <p class="eyebrow">Development sign in</p>
            <h2>Local admin access</h2>
            <p class="form-note">Use only for local development. Passwords are never echoed in errors.</p>
          </div>
          {#if authState === "checking"}
            <p class="status-message" role="status">Checking current session…</p>
          {/if}
          {#if errorMessage && authState !== "registration-failed"}
            <p class="error-message" role="alert">{errorMessage}</p>
          {/if}
          <label>
            Username
            <input autocomplete="username" bind:value={username} name="username" required />
          </label>
          <label>
            Password
            <input autocomplete="current-password" bind:value={password} name="password" required type="password" />
          </label>
          <button class="primary-action submit-action" disabled={isSubmitting} type="submit">
            {isSubmitting ? "Signing in…" : "Log in as local admin"}
          </button>
        </form>
      </div>
    </section>

    <section class="learn-more" aria-labelledby="learn-more-heading">
      <p class="eyebrow">Learn more</p>
      <h2 id="learn-more-heading">Mirad and MiraLingo docs</h2>
      <div class="link-grid">
        {#each docsLinks as link}
          <a href={link.href}>
            <strong>{link.label}</strong>
            <span>{link.description}</span>
          </a>
        {/each}
      </div>
    </section>
  </main>
{/if}
