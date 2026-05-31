<script>
  import { onMount } from "svelte";
  import "./app.css";
  import { getPracticeAudioUrl } from "./lib/api/audio";
  import { deleteAccount, fetchCurrentUser, login, logout as logoutRequest, readJson, register } from "./lib/api/auth";
  import { getPracticeProgress, getPracticeQueue, submitPracticeAnswer } from "./lib/api/practice";
  import { getSettings, updateSettings } from "./lib/api/settings";
  import AppShell from "./lib/components/layout/AppShell.svelte";
  import StudyShell from "./lib/components/layout/StudyShell.svelte";
  import ExerciseCard from "./lib/components/learning/ExerciseCard.svelte";
  import AppButton from "./lib/components/ui/AppButton.svelte";
  import AppCard from "./lib/components/ui/AppCard.svelte";
  import AppInput from "./lib/components/ui/AppInput.svelte";
  import { authError, authState, currentUser, resetAuthStore, setAnonymous, setAuthenticated, setAuthFailure } from "./lib/stores/auth";
  import { currentSection, goToDashboard, resetPracticeNavigation, setCurrentSection, setPracticeMode } from "./lib/stores/practice";
  import { applySettingsPayload, resetSettingsStore, settingsLoadedForUser, theme, ttsSpeed } from "./lib/stores/settings";
  import Dashboard from "./lib/pages/Dashboard.svelte";
  import Welcome from "./lib/pages/Welcome.svelte";

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
  const navItemsFor = (section) => [
    { id: "dashboard", label: "Today", href: "#dashboard", active: section === "dashboard" },
    { id: "practice", label: "Practice", href: "#practice", active: practiceSection(section) },
    { id: "lexicon", label: "Lexicon", href: "#lexicon", active: section === "lexicon" },
    { id: "settings", label: "Settings", href: "#settings", active: section === "settings" },
  ];

  let username = $state("admin");
  let password = $state("");
  let regU = $state("");
  let regP = $state("");
  let submitting = $state(false);

  let practiceState = $state("idle");
  let practiceErr = $state("");
  let practiceQueueCards = $state([]);
  let practiceQueueIndex = $state(0);
  let practiceQueueMode = $state(null);
  let currentCard = $state(null);
  let typedAnswer = $state("");
  let answerErr = $state("");
  let answerSubmitting = $state(false);
  let answerResult = $state(null);
  let miradAudioUnlocked = $state(false);
  let activeCardId = $state(null);

  let audioState = $state("idle");
  let audioMsg = $state("");
  let audioBlobUrl = $state("");
  let activeAudio = $state(null);
  let lastAudioCardId = $state(null);

  let analyticsState = $state("idle");
  let analyticsErr = $state("");
  let analyticsPayload = $state(null);

  let settingsState = $state("idle");
  let settingsErr = $state("");
  let settingsStatus = $state("");
  let settingsPhase = $state("");

  let deleteAccountState = $state("idle");
  let deleteAccountErr = $state("");
  let deleteAccountStatus = $state("");
  let deleteAccountConfirm = $state("");
  let deleteAccountUsername = $state("");

  function replaceHash(section) {
    if (typeof window === "undefined") return;
    window.history.replaceState(null, "", `#${section}`);
  }

  function applyTheme(themeValue) {
    if (typeof document === "undefined") return;
    document.documentElement.setAttribute("data-theme", coerceTheme(themeValue));
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
  };

  const resetAnswer = () => {
    typedAnswer = "";
    answerErr = "";
    answerResult = null;
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
    currentCard = null;
    activeCardId = null;
    lastAudioCardId = null;
  };

  const resetAnalyticsSurface = () => {
    analyticsState = "idle";
    analyticsErr = "";
    analyticsPayload = null;
  };

  const resetSettingsSurface = () => {
    settingsState = "idle";
    settingsErr = "";
    settingsStatus = "";
    settingsPhase = "";
    resetSettingsStore();
    deleteAccountState = "idle";
    deleteAccountErr = "";
    deleteAccountStatus = "";
    deleteAccountUsername = "";
    deleteAccountConfirm = "";
  };

  const syncSettings = (payload, extra = {}) => {
    applySettingsPayload(payload ?? {});
    if (extra.state) settingsState = extra.state;
    if (extra.phase) settingsPhase = extra.phase;
    if (extra.msg) settingsStatus = extra.msg;
  };

  async function loadCurrentUser() {
    authError.set("");
    try {
      const { response, payload } = await fetchCurrentUser();
      if (response.ok && payload.authenticated && payload.user) {
        setAuthenticated(payload.user);
        resetPracticeSurface();
        resetAnalyticsSurface();
        resetSettingsSurface();
        deleteAccountUsername = payload.user.username ?? "";
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
      const { response, payload } = await login(username, password);
      if (!response.ok || !payload.authenticated || !payload.user) {
        setAuthFailure("login-failed", payload?.detail ?? "Login failed.");
        return;
      }
      setAuthenticated(payload.user);
      password = "";
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      deleteAccountUsername = payload.user.username ?? "";
      await loadSettings({ force: true });
      await preloadPracticeQueue("mixed");
      navigateToSection("dashboard");
    } catch (_) {
      setAuthFailure("login-failed", "Could not reach MiraLingo auth.");
    } finally {
      submitting = false;
    }
  }

  async function submitRegistration() {
    submitting = true;
    authError.set("");
    try {
      const { response, payload } = await register(regU, regP);
      if (!response.ok || !payload.authenticated || !payload.user) {
        setAuthFailure("registration-failed", payload?.detail ?? "Registration failed.");
        return;
      }
      setAuthenticated(payload.user);
      regP = "";
      resetPracticeSurface();
      resetAnalyticsSurface();
      resetSettingsSurface();
      deleteAccountUsername = payload.user.username ?? "";
      await loadSettings({ force: true });
      await preloadPracticeQueue("mixed");
      navigateToSection("dashboard");
    } catch (_) {
      setAuthFailure("registration-failed", "Could not reach MiraLingo registration.");
    } finally {
      submitting = false;
    }
  }

  function clearAuthAppState(message = "") {
    resetPracticeSurface();
    resetAnalyticsSurface();
    resetSettingsSurface();
    username = "admin";
    password = "";
    regU = "";
    regP = "";
    resetPracticeNavigation();
    resetAuthStore(message);
    replaceHash("welcome");
  }

  async function logout() {
    try {
      await logoutRequest();
    } finally {
      clearAuthAppState();
    }
  }

  async function loadSettings({ force = false } = {}) {
    if (settingsState === "loading" || settingsState === "saving") return;
    if (!force && $settingsLoadedForUser === $currentUser?.username && settingsState !== "idle") return;

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
      settingsLoadedForUser.set($currentUser?.username ?? null);
    } catch (_) {
      settingsLoadedForUser.set($currentUser?.username ?? null);
      applySettingsPayload({});
      settingsState = "error";
      settingsPhase = "settings_get";
      settingsErr = "Could not reach saved settings.";
    }
  }

  async function saveSettings() {
    if (settingsState === "saving") return;

    settingsState = "saving";
    settingsPhase = "settings_update";
    settingsErr = "";
    settingsStatus = "Saving…";

    try {
      const body = { theme: coerceTheme($theme), tts_speed: coerceSpeed($ttsSpeed) };
      const { response, payload } = await updateSettings(body);
      if (!response.ok || payload.ok === false) {
        settingsState = "error";
        settingsPhase = payload?.phase ?? "settings_update";
        settingsErr = payload?.detail ?? "Could not save.";
        settingsStatus = "";
        return;
      }
      syncSettings(payload.settings, { state: "ready", phase: payload.phase ?? "settings_update", msg: "Saved." });
      settingsLoadedForUser.set($currentUser?.username ?? $settingsLoadedForUser);
    } catch (_) {
      settingsState = "error";
      settingsPhase = "settings_update";
      settingsErr = "Could not save settings.";
      settingsStatus = "";
    }
  }

  async function loadPracticeQueue(mode = "mixed", options = {}) {
    const silent = options.silent === true;
    if (!silent) {
      practiceState = "loading";
      practiceErr = "";
    }

    try {
      const { response, payload } = await getPracticeQueue(mode, 50);
      if (!response.ok || payload.ok === false) {
        practiceState = "error";
        practiceErr = payload?.detail ?? "Could not load practice cards.";
        return;
      }

      const cards = Array.isArray(payload.cards) ? payload.cards : [];
      practiceQueueCards = cards;
      practiceQueueIndex = 0;
      practiceQueueMode = mode;
      currentCard = cards[0] ?? null;
      practiceState = cards.length ? "ready" : "empty";
      practiceErr = cards.length ? "" : "No cards. Import content first.";
      resetAnswer();
      resetAudio();
    } catch (_) {
      practiceState = "error";
      practiceErr = "Could not load practice cards.";
    }
  }

  async function preloadPracticeQueue(mode = "mixed") {
    if (practiceQueueMode === mode && practiceQueueCards.length > 0) return;
    await loadPracticeQueue(mode, { silent: true });
  }

  async function openPracticeMode(mode) {
    setPracticeMode(mode);
    replaceHash(mode === "mixed" ? "practice" : mode);
    await loadPracticeQueue(mode);
  }

  function goToMenu() {
    goToDashboard();
    replaceHash("dashboard");
    resetPracticeSurface();
  }

  async function advancePracticeCard() {
    if (practiceQueueIndex + 1 < practiceQueueCards.length) {
      practiceQueueIndex += 1;
      currentCard = practiceQueueCards[practiceQueueIndex] ?? null;
      return;
    }
    await loadPracticeQueue(practiceQueueMode ?? "mixed");
  }

  async function recordAnswer(body) {
    answerSubmitting = true;
    answerErr = "";
    practiceErr = "";

    try {
      const { response, payload } = await submitPracticeAnswer(body);
      if (!response.ok || payload.ok === false) {
        practiceErr = payload?.detail ?? "Could not record answer.";
        return;
      }
      answerResult = payload;
      miradAudioUnlocked = true;
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
    await recordAnswer({ card_id: currentCard.id, answer });
  }

  async function submitGiveUp() {
    if (!currentCard?.id) return;
    answerErr = "";
    await recordAnswer({ card_id: currentCard.id, correct: false });
  }

  async function playCardAudio() {
    if (!currentCard) return;
    resetAudio();
    audioState = "loading";

    try {
      const cardId = currentCard.audio_card_id ?? currentCard.base_card_id ?? currentCard.id;
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

  async function loadAnalytics() {
    analyticsState = "loading";
    analyticsErr = "";

    try {
      const { response, payload } = await getPracticeProgress();
      if (!response.ok || payload.ok === false) {
        analyticsPayload = payload;
        analyticsState = "error";
        analyticsErr = payload?.detail ?? "Analytics unavailable.";
        return;
      }
      analyticsPayload = payload;
      analyticsState = "ready";
    } catch (_) {
      analyticsState = "error";
      analyticsErr = "Analytics unavailable.";
    }
  }

  async function submitDeleteAccount() {
    if (!canSubmitDelete()) return;

    deleteAccountState = "submitting";
    deleteAccountErr = "";
    deleteAccountStatus = "";

    try {
      const { response, payload } = await deleteAccount(deleteAccountUsername, deleteAccountConfirm);
      if (!response.ok || payload.ok === false) {
        deleteAccountState = "error";
        deleteAccountErr = payload?.detail ?? "Could not delete account.";
        return;
      }
      deleteAccountStatus = `Deleted ${payload?.deleted_username ?? deleteAccountUsername}.`;
      clearAuthAppState("Account deleted.");
    } catch (_) {
      deleteAccountState = "error";
      deleteAccountErr = "Could not delete account.";
    }
  }

  const canDeleteAccount = () => ($currentUser?.username ?? "") !== "admin";
  const deleteConfirmPhrase = () => `${$currentUser?.username ?? ""} DELETE`.trim();
  const canSubmitDelete = () => (
    deleteAccountUsername.trim() === ($currentUser?.username ?? "") && deleteAccountConfirm.trim() === deleteConfirmPhrase()
  );

  async function navigateToSection(section) {
    if ($authState !== "authenticated") return;

    if (section === "dashboard") {
      goToDashboard();
      replaceHash("dashboard");
      resetPracticeSurface();
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

    resetAudio();
    resetAnswer();
    setCurrentSection(section);
    replaceHash(section);

    if (section === "analytics") {
      await loadAnalytics();
      return;
    }

    if (section === "settings") {
      deleteAccountUsername = $currentUser?.username ?? deleteAccountUsername;
      await loadSettings();
    }
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

    void navigateToSection("dashboard");
  }

  $effect(() => {
    if (currentCard?.id !== activeCardId) {
      activeCardId = currentCard?.id ?? null;
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

  $effect(() => {
    applyTheme($theme);
  });

  onMount(() => {
    void loadCurrentUser();
  });
</script>

<svelte:head>
  <title>MiraLingo</title>
  <meta name="description" content="Practice Mirad." />
</svelte:head>

<svelte:window on:hashchange={() => syncRouteFromHash()} />

{#if $authState === "authenticated" && practiceSection($currentSection)}
  <StudyShell
    title={practiceTitle($currentSection)}
    subtitle="Focused study mode"
    userLabel="Study mode"
    avatarLabel={$currentUser?.username ?? "Learner"}
    backLabel="Back to today"
    on:click={goToMenu}
  >
    <svelte:fragment slot="status">
      {#if practiceState === "loading"}
        <p class="mb-4 text-center text-sm text-slate-500 dark:text-slate-400">Loading practice queue…</p>
      {:else if practiceState === "empty"}
        <p class="mb-4 text-center text-sm text-slate-500 dark:text-slate-400">No cards. Import content first.</p>
      {:else if practiceState === "error"}
        <p class="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300" role="alert">{practiceErr}</p>
      {/if}
    </svelte:fragment>

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
    />
  </StudyShell>
{:else if $authState === "authenticated" && $currentSection === "dashboard"}
  <Dashboard
    userName={$currentUser?.username ?? "Learner"}
    activeSection={$currentSection}
    on:continuePractice={() => navigateToSection("practice")}
    on:revision={() => navigateToSection("revision")}
    on:buildVocabulary={() => navigateToSection("build_vocabulary")}
    on:lexicon={() => navigateToSection("lexicon")}
  />
{:else if $authState === "authenticated" && $currentSection === "analytics"}
  <AppShell
    title="Analytics"
    subtitle="Current backend progress, without API reshaping"
    showBackButton={true}
    backLabel="Back to today"
    userLabel="Progress"
    avatarLabel={$currentUser?.username ?? "Learner"}
    navItems={navItemsFor($currentSection)}
    on:click={goToMenu}
  >
    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {#if analyticsState === "loading"}
        <AppCard className="sm:col-span-2 xl:col-span-3">
          <p class="text-sm text-slate-500 dark:text-slate-400">Loading analytics…</p>
        </AppCard>
      {:else if analyticsErr}
        <AppCard className="sm:col-span-2 xl:col-span-3 border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
          <p role="alert">{analyticsErr}</p>
        </AppCard>
      {:else if analyticsPayload}
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Answered</p><p class="mt-3 text-3xl font-semibold">{fmtN(analyticsPayload.event_count ?? 0)}</p></AppCard>
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Accuracy</p><p class="mt-3 text-3xl font-semibold">{fmtPct(analyticsPayload.accuracy)}</p></AppCard>
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Weak cards</p><p class="mt-3 text-3xl font-semibold">{fmtN(analyticsPayload.weak_count ?? 0)}</p></AppCard>
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Mastered</p><p class="mt-3 text-3xl font-semibold">{fmtN(analyticsPayload.mastered_count ?? 0)}</p></AppCard>
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Stale</p><p class="mt-3 text-3xl font-semibold">{fmtN(analyticsPayload.stale_count ?? 0)}</p></AppCard>
        <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">New</p><p class="mt-3 text-3xl font-semibold">{fmtN(analyticsPayload.new_count ?? 0)}</p></AppCard>
      {:else}
        <AppCard className="sm:col-span-2 xl:col-span-3">
          <p class="text-sm text-slate-500 dark:text-slate-400">No analytics yet.</p>
        </AppCard>
      {/if}
    </div>

    <svelte:fragment slot="sidebar">
      <AppCard className="space-y-3">
        <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Refresh from backend</p>
        <p class="text-sm text-slate-500 dark:text-slate-400">This surface stays honest to the existing <code>/practice/progress</code> response.</p>
        <AppButton variant="secondary" className="min-h-12 w-full justify-center" on:click={loadAnalytics} disabled={analyticsState === "loading"}>
          {analyticsState === "loading" ? "Refreshing…" : "Refresh analytics"}
        </AppButton>
      </AppCard>
    </svelte:fragment>
  </AppShell>
{:else if $authState === "authenticated" && $currentSection === "settings"}
  <AppShell
    title="Settings"
    subtitle="Personalize theme and speech speed"
    showBackButton={true}
    backLabel="Back to today"
    userLabel={settingsPhase || "Settings"}
    avatarLabel={$currentUser?.username ?? "Learner"}
    navItems={navItemsFor($currentSection)}
    on:click={goToMenu}
  >
    <div class="space-y-4">
      {#if settingsErr}
        <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"><p role="alert">{settingsErr}</p></AppCard>
      {/if}
      {#if settingsStatus}
        <AppCard className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"><p>{settingsStatus}</p></AppCard>
      {/if}
      {#if deleteAccountErr}
        <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"><p role="alert">{deleteAccountErr}</p></AppCard>
      {/if}
      {#if deleteAccountStatus}
        <AppCard className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"><p>{deleteAccountStatus}</p></AppCard>
      {/if}

      <AppCard>
        <form class="space-y-6" onsubmit={(event) => { event.preventDefault(); saveSettings(); }}>
          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">Theme</legend>
            <div class="grid gap-3 sm:grid-cols-3">
              {#each [{ v: "system", l: "System" }, { v: "light", l: "Light" }, { v: "dark", l: "Dark" }] as option}
                <label class="flex cursor-pointer items-center gap-3 rounded-2xl border border-violet-100 px-4 py-3 text-sm font-medium dark:border-violet-900/60">
                  <input bind:group={$theme} type="radio" value={option.v} />
                  <span>{option.l}</span>
                </label>
              {/each}
            </div>
          </fieldset>

          <fieldset class="space-y-3">
            <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">TTS speed: {spd($ttsSpeed)}</legend>
            <div class="grid gap-3 sm:grid-cols-5">
              {#each [0.7, 0.8, 0.9, 1.0, 1.1] as option}
                <label class="flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-violet-100 px-4 py-3 text-sm font-medium dark:border-violet-900/60">
                  <input bind:group={$ttsSpeed} type="radio" value={option} />
                  <span>{spd(option)}</span>
                </label>
              {/each}
            </div>
          </fieldset>

          <AppButton type="submit" className="min-h-12 justify-center" disabled={settingsState === "saving"}>
            {settingsState === "saving" ? "Saving…" : "Save settings"}
          </AppButton>
        </form>
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
            <AppInput id="del-username" label="Username" bind:value={deleteAccountUsername} autocomplete="username" />
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
{:else if $authState === "authenticated" && $currentSection === "lexicon"}
  <AppShell
    title="Lexicon"
    subtitle="Search will land here without changing backend contracts"
    showBackButton={true}
    backLabel="Back to today"
    userLabel="Placeholder"
    avatarLabel={$currentUser?.username ?? "Learner"}
    navItems={navItemsFor($currentSection)}
    on:click={goToMenu}
  >
    <AppCard className="space-y-3">
      <p class="text-lg font-semibold text-slate-900 dark:text-slate-100">Lexicon Search</p>
      <p class="text-sm text-slate-500 dark:text-slate-400">The dashboard can route here now. Search UI can be added in a later slice without reworking the section router.</p>
      <AppButton variant="secondary" className="min-h-12 justify-center" on:click={() => navigateToSection("dashboard")}>Return to Today</AppButton>
    </AppCard>
  </AppShell>
{:else}
  <Welcome
    bind:loginUsername={username}
    bind:loginPassword={password}
    bind:registrationUsername={regU}
    bind:registrationPassword={regP}
    {submitting}
    authState={$authState}
    authError={$authError}
    on:createAccount={submitRegistration}
    on:logIn={submitLogin}
  />
{/if}
