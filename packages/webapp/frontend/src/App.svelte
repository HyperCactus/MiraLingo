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

  const friendlyAuthError = (payload, fallback) => {
    if (payload?.detail) return payload.detail;
    if (payload?.error === "invalid_credentials") return "Invalid username or password.";
    if (payload?.error === "local_admin_disabled") {
      return "Local admin login is only available when development bootstrap is enabled.";
    }
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
          Your local development account is ready for Mirad pronunciation, translation, and vocabulary
          practice flows as they come online.
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
          <dt>Mode</dt>
          <dd>Local development</dd>
        </div>
      </dl>
      <div class="practice-grid" aria-label="Practice areas">
        <article>
          <span aria-hidden="true">↔</span>
          <h2>Translation drills</h2>
          <p>Move between English and Mirad with feedback from the translator engine.</p>
        </article>
        <article>
          <span aria-hidden="true">♪</span>
          <h2>Pronunciation</h2>
          <p>Prepare for TTS-backed listening and speaking practice.</p>
        </article>
        <article>
          <span aria-hidden="true">✦</span>
          <h2>Vocabulary</h2>
          <p>Build a future spaced-repetition loop around Mirad roots and compounds.</p>
        </article>
      </div>
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
