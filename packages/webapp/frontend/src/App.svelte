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

  let username = "admin";
  let password = "";
  let registerUsername = "";
  let registerPassword = "";
  let authState = "checking";
  let user = null;
  let errorMessage = "";
  let isSubmitting = false;
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

  async function readJson(response) {
    try {
      return await response.json();
    } catch (_error) {
      return {};
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
        await loadPracticeQueue();
        return;
      }
      user = null;
      authState = "anonymous";
    } catch (_error) {
      user = null;
      authState = "anonymous";
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
      await loadPracticeQueue();
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
      await loadPracticeQueue();
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
      resetAudioState();
      resetAnswerState();
      user = null;
      username = "admin";
      password = "";
      registerUsername = "";
      registerPassword = "";
      authState = "anonymous";
      practiceState = "idle";
      practiceQueue = null;
      currentCard = null;
      activeCardId = null;
      lastAudioCardId = null;
      practiceError = "";
    }
  }

  async function loadPracticeQueue() {
    resetAudioState();
    practiceState = "loading";
    practiceError = "";
    try {
      const response = await fetch("/practice/queue?mode=mixed&limit=3", { headers: { Accept: "application/json" } });
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
      activeAudio.addEventListener("ended", () => {
        audioState = "idle";
        audioMessage = "Audio finished.";
      });
      await activeAudio.play();
      audioState = "playing";
      audioMessage = "Playing Mirad audio.";
    } catch (_error) {
      audioState = "error";
      audioMessage = "Could not play audio. Check the server, then try again.";
      audioDiagnostic = "network_or_browser_playback";
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
          Request an adaptive Mirad practice queue, type the answer you recall, and reveal the
          backend-scored result without clutter from progress analytics.
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
          <dt>Queue events</dt>
          <dd>{practiceQueue?.event_count ?? 0}</dd>
        </div>
      </dl>

      <section class="practice-panel" aria-labelledby="practice-heading">
        <div class="practice-header">
          <div>
            <p class="eyebrow">Adaptive session</p>
            <h2 id="practice-heading">Practice queue</h2>
          </div>
          <button class="secondary-action" type="button" on:click={loadPracticeQueue} disabled={practiceState === "loading" || answerSubmitting}>
            {practiceState === "loading" ? "Loading…" : "Refresh queue"}
          </button>
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

      <button class="secondary-action" type="button" on:click={logout}>Log out</button>
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
