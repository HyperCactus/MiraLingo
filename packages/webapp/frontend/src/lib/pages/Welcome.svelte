<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  const dispatch = createEventDispatcher<{
    createAccount: void;
    logIn: void;
    jumpCreateAccount: void;
    jumpLogin: void;
  }>();

  export let loginUsername = 'admin';
  export let loginPassword = '';
  export let registrationUsername = '';
  export let registrationPassword = '';
  export let submitting = false;
  export let authState = 'anonymous';
  export let authError = '';

  const previewCards = [
    {
      eyebrow: 'Guided practice',
      title: 'Switch between recall directions',
      body: 'Move from English prompts into Mirad answers, then reinforce pronunciation with reveal-aware audio.',
    },
    {
      eyebrow: 'Today dashboard',
      title: 'See the next best study action',
      body: 'Continue practice, revisit weaker cards, or build vocabulary from one mobile-first home screen.',
    },
    {
      eyebrow: 'Honest progress',
      title: 'Keep backend metrics intact',
      body: 'The new landing experience stays UI-focused while preserving the current auth and practice API behavior.',
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
            MiraLingo introduces the Mirad language through short study sessions that pair translation recall, pronunciation support, and an honest today-first dashboard.
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
          {#each previewCards as card}
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
            <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Why Mirad works here</p>
            <p class="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">
              Start with a calm intro, then move into lightweight account creation or sign-in without leaving the landing flow.
            </p>
          </div>
          <ul class="space-y-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Short, mobile-friendly practice cards keep the next answer in focus.</li>
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Reveal-aware Mirad audio supports pronunciation without spoiling prompts early.</li>
            <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Today, Revision, and Build Vocabulary flows stay aligned with the existing backend data.</li>
          </ul>
        </AppCard>

        <AppCard className="space-y-2">
          <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Mirad language intro</p>
          <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">
            Mirad is a constructed language designed for international clarity. MiraLingo keeps the onboarding simple so new learners can hear, read, and recall vocabulary quickly.
          </p>
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
          <form class="space-y-4" on:submit|preventDefault={() => dispatch('createAccount')}>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Username</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="username" bind:value={registrationUsername} required />
            </label>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Password</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="new-password" bind:value={registrationPassword} required type="password" />
            </label>
            <AppButton type="submit" className="min-h-12 w-full justify-center">{submitting ? 'Creating…' : 'Create Account'}</AppButton>
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
          <form class="space-y-4" on:submit|preventDefault={() => dispatch('logIn')}>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Username</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="username" bind:value={loginUsername} required />
            </label>
            <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
              <span>Password</span>
              <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="current-password" bind:value={loginPassword} required type="password" />
            </label>
            <AppButton type="submit" className="min-h-12 w-full justify-center">{submitting ? 'Signing in…' : 'Log In'}</AppButton>
          </form>
        </AppCard>
      </div>
    </section>
  </main>
</div>
