<script lang="ts">
  import { onMount } from 'svelte';
  import { getPracticeAnalytics, type PracticeAnalyticsResponse } from '../api/practice';
  import AppShell from '../components/layout/AppShell.svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  export let userName = 'Learner';
  export let activeSection = 'analytics';
  export let navItems: { id: string; label: string; href: string; active?: boolean }[] = [];
  export let onBack: () => void = () => {};
  export let onSettings: () => void = () => {};
  export let onLogout: () => void = () => {};

  let state: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let error = '';
  let payload: PracticeAnalyticsResponse | null = null;

  const n = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? v : 0);
  const pct = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? `${Math.round(v * 100)}%` : '0%');
  const obj = (v: unknown) => (v && typeof v === 'object' ? (v as Record<string, unknown>) : {});
  const rows = (v: unknown[]) => (Array.isArray(v) ? v : []);

  $: timing = obj(payload?.timing);
  $: streak = obj(payload?.streak);
  $: lifecycle = obj(payload?.lifecycle);
  $: direction = obj(payload?.direction_breakdown);
  $: cardTypes = obj(payload?.card_type_breakdown);
  $: perCard = rows((payload?.per_card as unknown[]) ?? []);
  $: sparseHistory = Boolean(payload?.sparse_history) || (n(payload?.event_count) === 0 && n(payload?.session_count) === 0 && n(payload?.lifecycle_count) === 0);

  async function loadAnalytics() {
    state = payload ? 'ready' : 'loading';
    error = '';
    try {
      const { response, payload: next } = await getPracticeAnalytics();
      payload = next;
      if (!response.ok || next.ok === false) {
        state = 'error';
        error = next.detail ?? 'Analytics unavailable.';
        return;
      }
      state = 'ready';
    } catch (_e) {
      state = 'error';
      error = 'Analytics unavailable.';
    }
  }

  onMount(() => {
    void loadAnalytics();
  });
</script>

<AppShell
  title="Analytics"
  subtitle="Detailed backend practice analytics"
  showBackButton={true}
  backLabel="Back to today"
  userLabel="Progress"
  avatarLabel={userName}
  {navItems}
  on:click={onBack}
  on:settings={onSettings}
  on:logout={onLogout}
>
  {#if state === 'error'}
    <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
      <p role="alert">{error}</p>
    </AppCard>
  {:else if sparseHistory}
    <AppCard>
      <p class="text-sm text-slate-500 dark:text-slate-400">Sparse history: complete more practice sessions to unlock deeper analytics.</p>
    </AppCard>
  {/if}

  <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Answered</p><p class="mt-3 text-3xl font-semibold">{n(payload?.event_count)}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Accuracy</p><p class="mt-3 text-3xl font-semibold">{pct(payload?.accuracy)}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Sessions</p><p class="mt-3 text-3xl font-semibold">{n(payload?.session_count)}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Lifecycles</p><p class="mt-3 text-3xl font-semibold">{n(payload?.lifecycle_count)}</p></AppCard>
  </div>

  <AppCard className="mt-4 overflow-auto">
    <p class="mb-2 text-sm font-semibold">Per-card breakdown</p>
    {#if perCard.length === 0}
      <p class="text-sm text-slate-500 dark:text-slate-400">No analytics yet.</p>
    {:else}
      <table class="min-w-full text-sm">
        <thead><tr><th class="text-left">Card</th><th>Seen</th><th>Correct</th></tr></thead>
        <tbody>
          {#each perCard as row}
            {@const r = obj(row)}
            <tr><td>{String(r.card_id ?? 'unknown')}</td><td>{n(r.seen)}</td><td>{n(r.correct)}</td></tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </AppCard>

  <svelte:fragment slot="sidebar">
    <AppCard className="space-y-3">
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Refresh from backend</p>
      <AppButton variant="secondary" className="min-h-12 w-full justify-center" on:click={loadAnalytics} disabled={state === 'loading'}>
        {state === 'loading' ? 'Refreshing…' : 'Refresh analytics'}
      </AppButton>
      <dl class="space-y-2 text-xs text-slate-500 dark:text-slate-400">
        <div><dt>Timing keys</dt><dd>{Object.keys(timing).length}</dd></div>
        <div><dt>Streak keys</dt><dd>{Object.keys(streak).length}</dd></div>
        <div><dt>Lifecycle keys</dt><dd>{Object.keys(lifecycle).length}</dd></div>
        <div><dt>Direction keys</dt><dd>{Object.keys(direction).length}</dd></div>
        <div><dt>Card type keys</dt><dd>{Object.keys(cardTypes).length}</dd></div>
      </dl>
    </AppCard>
  </svelte:fragment>
</AppShell>
