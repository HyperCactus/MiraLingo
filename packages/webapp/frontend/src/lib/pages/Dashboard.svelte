<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { getPracticeSummary, type PracticeSummaryResponse } from '../api/practice';
  import AppShell from '../components/layout/AppShell.svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';
  import AppProgressBar from '../components/ui/AppProgressBar.svelte';

  const dispatch = createEventDispatcher<{
    continuePractice: void;
    revision: void;
    buildVocabulary: void;
    lexicon: void;
    settings: void;
    analytics: void;
    admin: void;
    logout: void;
  }>();

  export let userName = 'Learner';
  export let activeSection = 'dashboard';
  export let refreshSignal = 0;
  export let showAdmin = false;

  let state: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let error = '';
  let summary: PracticeSummaryResponse | null = null;

  $: navItems = [
    { id: 'dashboard', label: 'Today', href: '#dashboard', active: activeSection === 'dashboard' },
    { id: 'practice', label: 'Practice', href: '#practice', active: activeSection === 'practice' },
    { id: 'lexicon', label: 'Lexicon', href: '#lexicon', active: activeSection === 'lexicon' },
    { id: 'settings', label: 'Settings', href: '#settings', active: activeSection === 'settings' },
    ...(showAdmin ? [{ id: 'admin', label: 'Admin', href: '#admin', active: activeSection === 'admin' }] : []),
  ];

  const safeCount = (value: unknown) => (typeof value === 'number' && Number.isFinite(value) ? value : 0);

  $: streak = summary?.streak && typeof summary.streak === 'object' ? summary.streak as Record<string, unknown> : {};
  $: currentStreak = safeCount(streak.current_days);
  $: masteredCountUnified = safeCount(summary?.mastered_count);
  $: activeDeckCount = safeCount(summary?.active_deck_count ?? summary?.active_count);
  $: progressAccuracy = typeof summary?.accuracy === 'number' && Number.isFinite(summary.accuracy)
    ? Math.round(summary.accuracy * 100)
    : 0;

  async function loadProgress() {
    state = summary ? 'ready' : 'loading';
    error = '';
    try {
      const { response, payload } = await getPracticeSummary();
      if (response.status === 401) {
        dispatch('logout');
        return;
      }
      if (!response.ok || payload.ok === false) {
        state = 'error';
        error = payload.detail ?? 'Could not load today\'s progress.';
        if (!summary) summary = payload;
        return;
      }
      summary = payload;
      state = 'ready';
    } catch (_error) {
      state = 'error';
      error = 'Could not load today\'s progress.';
    }
  }

  let refreshTimer: ReturnType<typeof setTimeout> | null = null;

  $: if (refreshSignal > 0) {
    if (refreshTimer) clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => {
      void loadProgress();
      refreshTimer = null;
    }, 350);
  }

  onMount(() => {
    void loadProgress();
  });
</script>

<AppShell
  title="Today"
  subtitle="Your next Mirad study actions"
  userLabel="Logged in"
  avatarLabel={userName}
  {navItems}
  {showAdmin}
  on:click
  on:settings={() => dispatch('settings')}
  on:admin={() => dispatch('admin')}
  on:logout={() => dispatch('logout')}
>
  <svelte:fragment slot="hero">
    <AppCard className="space-y-5 bg-gradient-to-br from-violet-600 via-violet-500 to-fuchsia-500 text-white shadow-lg">
      <div class="space-y-2">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-violet-100">Welcome back</p>
        <h1 class="text-3xl font-semibold leading-tight sm:text-4xl">Hello, {userName}.</h1>
        <p class="max-w-2xl text-sm leading-6 text-violet-50/90 sm:text-base">
          Continue your practice streak, revisit weaker cards, or grow your working vocabulary with the next focused study block.
        </p>
      </div>

      <div class="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
        <div class="space-y-2">
          <p class="text-sm font-medium text-violet-100">Next step</p>
          <p class="text-lg font-semibold">Continue Practice</p>
        </div>
        <AppButton className="min-h-12 justify-center border border-slate-950/10 bg-slate-950 text-white shadow-lg shadow-slate-950/15 hover:bg-slate-800 focus-visible:ring-white dark:border-white/10 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100" on:click={() => dispatch('continuePractice')}>
          Continue Practice
        </AppButton>
      </div>
    </AppCard>
  </svelte:fragment>

  <div class="grid gap-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
    <AppCard className="space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Today at a glance</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Progress from your recent practice answers.</p>
        </div>
      </div>

      {#if state === 'error'}
        <div class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">{error}</div>
      {:else}
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl border border-violet-100 bg-violet-50/70 p-4 dark:border-violet-900/60 dark:bg-violet-950/40">
            <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">Practice volume</p>
            <p class="mt-3 text-3xl font-semibold text-slate-900 dark:text-slate-50">{safeCount(summary?.event_count)}</p>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Cards answered in the tracked progress history.</p>
          </div>

          <div class="rounded-2xl border border-violet-100 bg-violet-50/70 p-4 dark:border-violet-900/60 dark:bg-violet-950/40">
            <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">Accuracy</p>
            <p class="mt-3 text-3xl font-semibold text-slate-900 dark:text-slate-50">{progressAccuracy}%</p>
            <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">Correct answers out of total answers.</p>
          </div>
        </div>

        <div class="space-y-3 rounded-2xl border border-violet-100 p-4 dark:border-violet-900/60">
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Momentum</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">Current distribution of your practice state.</p>
            </div>
            <span class="text-sm font-semibold text-violet-700 dark:text-violet-300">{currentStreak} day streak</span>
          </div>
          <AppProgressBar value={masteredCountUnified} max={Math.max(1, masteredCountUnified + activeDeckCount)} showLabel={true} />
          <div class="grid gap-3 text-sm text-slate-600 dark:text-slate-300 sm:grid-cols-3">
            <div class="rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-900/60"><span class="block text-xs uppercase tracking-[0.2em] text-slate-400">Mastered</span><strong class="mt-1 block text-lg text-slate-900 dark:text-slate-50">{masteredCountUnified}</strong></div>
            <div class="rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-900/60"><span class="block text-xs uppercase tracking-[0.2em] text-slate-400">Active</span><strong class="mt-1 block text-lg text-slate-900 dark:text-slate-50">{activeDeckCount}</strong></div>
            <div class="rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-900/60"><span class="block text-xs uppercase tracking-[0.2em] text-slate-400">Streak</span><strong class="mt-1 block text-lg text-slate-900 dark:text-slate-50">{currentStreak} days</strong></div>
          </div>
        </div>
      {/if}
    </AppCard>

    <AppCard className="space-y-3">
      <div>
        <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Quick actions</p>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Jump straight into the practice mode you need next.</p>
      </div>
      <AppButton variant="secondary" className="min-h-12 w-full justify-between" on:click={() => dispatch('revision')}>
        <span>Revision</span>
        <span aria-hidden="true">→</span>
      </AppButton>
      <AppButton variant="secondary" className="min-h-12 w-full justify-between" on:click={() => dispatch('buildVocabulary')}>
        <span>Build Vocabulary</span>
        <span aria-hidden="true">→</span>
      </AppButton>
      <AppButton variant="ghost" className="min-h-12 w-full justify-between border border-violet-200 text-violet-700 hover:bg-violet-50 dark:border-violet-900/60 dark:text-violet-300 dark:hover:bg-violet-950/30" on:click={() => dispatch('analytics')}>
        <span>View detailed analytics</span>
        <span aria-hidden="true">↗</span>
      </AppButton>
      <AppButton variant="ghost" className="min-h-12 w-full justify-between border border-slate-200 dark:border-slate-800" on:click={() => dispatch('lexicon')}>
        <span>Lexicon Search</span>
        <span aria-hidden="true">↗</span>
      </AppButton>
      <AppButton variant="ghost" className="min-h-12 w-full justify-between border border-red-200 text-red-700 hover:bg-red-50 dark:border-red-900/60 dark:text-red-300 dark:hover:bg-red-950/30" on:click={() => dispatch('logout')}>
        <span>Log out</span>
        <span aria-hidden="true">↘</span>
      </AppButton>
      <p class="text-xs leading-5 text-slate-400 dark:text-slate-500">Practice regularly to improve accuracy and move more cards into mastered.</p>
    </AppCard>
  </div>

  <svelte:fragment slot="sidebar">
    <AppCard className="space-y-3">
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Summary endpoint fields</p>
      <dl class="space-y-3 text-sm text-slate-600 dark:text-slate-300">
        <div class="flex items-center justify-between gap-4"><dt>Total events</dt><dd class="font-semibold text-slate-900 dark:text-slate-50">{safeCount(summary?.event_count)}</dd></div>
        <div class="flex items-center justify-between gap-4"><dt>Current streak</dt><dd class="font-semibold text-slate-900 dark:text-slate-50">{currentStreak}</dd></div>
        <div class="flex items-center justify-between gap-4"><dt>Mastered cards</dt><dd class="font-semibold text-slate-900 dark:text-slate-50">{masteredCountUnified}</dd></div>
      </dl>
    </AppCard>
  </svelte:fragment>
</AppShell>
