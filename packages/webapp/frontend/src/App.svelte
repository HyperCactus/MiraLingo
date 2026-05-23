<main class="welcome-shell" aria-labelledby="welcome-heading">
  <section class="welcome-card">
    <p class="eyebrow">Mirad learning lab</p>
    <h1 id="welcome-heading">Welcome to MiraLingo</h1>
    <p class="lede">
      Practice pronunciation, translation, and vocabulary with the Mirad tools in one place.
    </p>
  </section>
</main>

<style>
  :global(body) {
    margin: 0;
    font-family:
      Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f5f0e8;
    color: #1f2933;
  }

  .welcome-shell {
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 2rem;
  }

  .welcome-card {
    max-width: 42rem;
    padding: 3rem;
    border-radius: 1.5rem;
    background: #fffaf2;
    box-shadow: 0 24px 80px rgba(66, 45, 24, 0.14);
  }

  .eyebrow {
    margin: 0 0 0.75rem;
    color: #9a5b13;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  h1 {
    margin: 0;
    font-size: clamp(2.5rem, 8vw, 5rem);
    line-height: 0.95;
  }

  .lede {
    margin: 1.5rem 0 0;
    color: #52606d;
    font-size: 1.25rem;
    line-height: 1.6;
  }
</style>
