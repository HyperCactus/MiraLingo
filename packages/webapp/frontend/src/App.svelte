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
  let authState = "checking";
  let user = null;
  let errorMessage = "";
  let isSubmitting = false;
  let practiceState = "idle";
  let practiceError = "";
  let practiceQueue = null;
  let currentCard = null;
  let answerSubmitting = false;

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

  async function logout() {
    errorMessage = "";
    try {
      await fetch("/auth/logout", { method: "POST", headers: { Accept: "application/json" } });
    } finally {
      user = null;
      password = "";
      authState = "anonymous";
      practiceState = "idle";
      practiceQueue = null;
      currentCard = null;
      practiceError = "";
    }
  }

  async function loadPracticeQueue() {
    practiceState = "loading";
    practiceError = "";
    try {
      const response = await fetch("/practice/queue?limit=3", { headers: { Accept: "application/json" } });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        practiceQueue = payload;
        currentCard = null;
        practiceState = "error";
        practiceError = friendlyPracticeError(payload, "Practice queue is unavailable. Try again after checking the server.");
        return;
      }
      practiceQueue = payload;
      currentCard = payload.cards?.[0] ?? null;
      practiceState = currentCard ? "ready" : "empty";
    } catch (_error) {
      practiceState = "error";
      currentCard = null;
      practiceError = "Could not reach practice APIs. Check that the web server is running.";
    }
  }

  async function submitPracticeAnswer(correct) {
    if (!currentCard || answerSubmitting) return;
    answerSubmitting = true;
    practiceError = "";
    try {
      const response = await fetch("/practice/answers", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ card_id: currentCard.id, correct }),
      });
      const payload = await readJson(response);
      if (!response.ok || payload.ok === false) {
        practiceState = "error";
        practiceError = friendlyPracticeError(payload, "Answer rejected. Refresh the queue and try again.");
        return;
      }
      await loadPracticeQueue();
    } catch (_error) {
      practiceState = "error";
      practiceError = "Could not submit the practice answer. Check the server and try again.";
    } finally {
      answerSubmitting = false;
    }
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
          Request an adaptive Mirad practice queue, answer the current card, and watch the scheduler
          prioritize weak or stale content from your session history.
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
          <dt>Practice events</dt>
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
              <span>Reason: {currentCard.scheduler_reason}</span>
            </div>
            <p class="prompt-label">English prompt</p>
            <p class="prompt-text">{currentCard.prompt}</p>
            <details>
              <summary>Show Mirad answer</summary>
              <p>{currentCard.answer}</p>
            </details>
            <dl class="diagnostic-grid" aria-label="Practice diagnostics">
              <div>
                <dt>event_count</dt>
                <dd>{practiceQueue?.event_count ?? 0}</dd>
              </div>
              <div>
                <dt>scheduler_reason</dt>
                <dd>{currentCard.scheduler_reason}</dd>
              </div>
              <div>
                <dt>Mastery</dt>
                <dd>{currentCard.mastery?.correct ?? 0}/{currentCard.mastery?.attempts ?? 0} correct</dd>
              </div>
              <div>
                <dt>Recency</dt>
                <dd>{currentCard.recency?.last_seen_at ?? "new"}</dd>
              </div>
            </dl>
            <div class="answer-row" aria-label="Submit answer">
              <button class="primary-action" type="button" disabled={answerSubmitting} on:click={() => submitPracticeAnswer(true)}>
                {answerSubmitting ? "Submitting…" : "I knew it"}
              </button>
              <button class="secondary-action" type="button" disabled={answerSubmitting} on:click={() => submitPracticeAnswer(false)}>
                I missed it
              </button>
            </div>
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
          <a class="primary-action" href="#login-panel">Log in</a>
          <a class="secondary-action" href="mailto:admin@example.invalid?subject=MiraLingo%20account">
            Create account
          </a>
        </div>
        <p class="helper-text">
          Account creation is not open yet. In development, use the guarded local admin bootstrap when
          enabled by backend settings.
        </p>
      </div>

      <form id="login-panel" class="login-card" aria-label="Local admin login" on:submit|preventDefault={submitLogin}>
        <div>
          <p class="eyebrow">Development sign in</p>
          <h2>Local admin access</h2>
          <p class="form-note">Use only for local development. Passwords are never echoed in errors.</p>
        </div>
        {#if authState === "checking"}
          <p class="status-message" role="status">Checking current session…</p>
        {/if}
        {#if errorMessage}
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
