<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  const dispatch = createEventDispatcher<{
    createAccount: void;
    logIn: void;
    jumpCreateAccount: void;
    jumpLogin: void;
    googleLogin: void;
    forgotPassword: void;
  }>();

  let {
    loginEmail = $bindable(''),
    loginPassword = $bindable(''),
    registrationEmail = $bindable(''),
    registrationName = $bindable(''),
    registrationPassword = $bindable(''),
    submitting = false,
    authState = 'anonymous',
    authError = '',
    authMessage = '',
  } = $props();

  const previewCards = [
    {
      eyebrow: 'Practice',
      title: 'Learn with short cards',
      body: 'Translate, listen, and check your answer one small step at a time.',
    },
    {
      eyebrow: 'Review',
      title: 'Come back to tricky words',
      body: 'MiraLingo helps you revisit words that need more practice.',
    },
    {
      eyebrow: 'Vocabulary',
      title: 'Build confidence daily',
      body: 'Add new Mirad words gradually without feeling overwhelmed.',
    },
  ];
</script>

<div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50">
  <main class="mx-auto flex min-h-screen max-w-6xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8">
    <section class="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_minmax(320px,0.9fr)] lg:items-start">
      <AppCard className="space-y-6 bg-gradient-to-br from-violet-600 via-violet-500 to-fuchsia-500 text-white shadow-lg">
        <div class="space-y-3">
          <p class="text-sm font-semibold uppercase tracking-[0.3em] text-violet-100">Welcome to Mirad</p>
          <h1 class="max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl">Build confidence in Mirad with focused daily practice.</h1>
          <p class="max-w-2xl text-sm leading-7 text-violet-50/90 sm:text-base">
            MiraLingo helps you practice Mirad with short, friendly cards for translation, listening, and review.
          </p>
        </div>

        <div class="grid gap-3 sm:grid-cols-2">
          <AppButton className="min-h-12 justify-center border border-slate-950/20 bg-slate-950 text-white hover:bg-slate-800 focus-visible:ring-white dark:border-white/20 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100" on:click={() => dispatch('jumpCreateAccount')}>
            Create Account
          </AppButton>
          <AppButton variant="secondary" className="min-h-12 justify-center border-white/30 bg-white/10 text-white hover:bg-white/20 focus-visible:ring-white dark:border-white/20 dark:bg-white/10 dark:text-white" on:click={() => dispatch('jumpLogin')}>
            Log In
          </AppButton>
        </div>

        <div class="grid gap-3 sm:grid-cols-3">
          {#each previewCards as card (card.title)}
            <div class="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur">
              <p class="text-xs font-semibold uppercase tracking-[0.22em] text-violet-100">{card.eyebrow}</p>
              <p class="mt-3 text-lg font-semibold text-white">{card.title}</p>
              <p class="mt-2 text-sm leading-6 text-violet-50/90">{card.body}</p>
            </div>
          {/each}
        </div>
      </AppCard>

      <div class="space-y-4">
        <AppCard className="space-y-3">
          <div>
            <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Start simply</p>
            <p class="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
              Create an account or log in, then choose a short practice session.
            </p>
          </div>
          <ul class="space-y-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Practice with small cards you can finish quickly.</li>
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Listen to Mirad words after you reveal an answer.</li>
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Review words and phrases as you build confidence.</li>
          </ul>
        </AppCard>

        <AppCard className="space-y-2">
          <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Mirad language intro</p>
          <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">
            Mirad is a constructed language designed to be regular and clear. MiraLingo gives you a gentle way to practice reading, hearing, and remembering it.
          </p>
          <div class="flex flex-wrap gap-3 text-sm font-semibold text-violet-700 dark:text-violet-300">
            <a href="https://en.wikibooks.org/wiki/Mirad_Grammar" target="_blank" rel="noopener">Mirad Grammar</a>
          </div>
        </AppCard>
      </div>
    </section>

    <section class="grid gap-4 lg:grid-cols-2">
      <div id="create-account-card">
        <AppCard className="space-y-4">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.22em] text-violet-600 dark:text-violet-300">Create account</p>
            <h2 class="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-50">Start your study profile</h2>
          </div>
          {#if authError && authState === 'registration-failed'}
            <div class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300" role="alert">{authError}</div>
          {/if}
          <form class="space-y-4" onsubmit={(event) => { event.preventDefault(); dispatch('createAccount'); }}>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Email</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="email" bind:value={registrationEmail} required type="email" />
            </label>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Name or nickname <span class="font-normal text-slate-400">optional</span></span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="name" bind:value={registrationName} />
            </label>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Password</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="new-password" bind:value={registrationPassword} minlength="8" maxlength="128" required type="password" />
              <span class="text-xs font-normal text-slate-500 dark:text-slate-400">Password must be 8 to 128 characters.</span>
            </label>
            <p class="text-xs leading-5 text-slate-500 dark:text-slate-400">
              By creating an account, you agree to the
              <a class="font-semibold text-violet-700 underline decoration-violet-300 underline-offset-4 hover:text-violet-900 dark:text-violet-300 dark:hover:text-violet-100" href="#privacy">Privacy Policy</a>.
            </p>
            <AppButton type="submit" className="min-h-12 w-full justify-center">{submitting ? 'Creating…' : 'Create Account'}</AppButton>
            <AppButton type="button" variant="secondary" className="min-h-12 w-full justify-center" on:click={() => dispatch('googleLogin')}>Sign in with Google</AppButton>
          </form>
        </AppCard>
      </div>

      <div id="login-card">
        <AppCard className="space-y-4">
          <div>
            <p class="text-sm font-semibold uppercase tracking-[0.22em] text-violet-600 dark:text-violet-300">Log in</p>
            <h2 class="mt-2 text-2xl font-semibold text-slate-900 dark:text-slate-50">Continue where you left off</h2>
          </div>
          {#if authError && authState !== 'registration-failed'}
            <div class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300" role="alert">{authError}</div>
          {/if}
          {#if authMessage}
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200" role="status">{authMessage}</div>
          {/if}
          <form class="space-y-4" onsubmit={(event) => { event.preventDefault(); dispatch('logIn'); }}>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Email</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="email" bind:value={loginEmail} required type="email" />
            </label>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Password</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="current-password" bind:value={loginPassword} required type="password" />
            </label>
            <AppButton type="submit" className="min-h-12 w-full justify-center">{submitting ? 'Signing in…' : 'Log In'}</AppButton>
            <AppButton type="button" variant="secondary" className="min-h-12 w-full justify-center" on:click={() => dispatch('googleLogin')}>Sign in with Google</AppButton>
            <button type="button" class="w-full text-sm font-semibold text-violet-700 hover:text-violet-900 dark:text-violet-300 dark:hover:text-violet-100" onclick={() => dispatch('forgotPassword')}>Forgot password?</button>
          </form>
        </AppCard>
      </div>
    </section>
  </main>
</div>
