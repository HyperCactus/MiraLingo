<script lang="ts">
  import { onMount } from 'svelte';
  import { getPracticeAnalytics, getPracticeProgress, type PracticeAnalyticsResponse, type PracticeProgressResponse } from '../api/practice';
  import AppShell from '../components/layout/AppShell.svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  export let userName = 'Learner';
  export let activeSection = 'analytics';
  export let navItems: { id: string; label: string; href: string; active?: boolean }[] = [];
  $: effectiveNavItems = navItems.length > 0 ? navItems : [
    { id: 'dashboard', label: 'Today', href: '#dashboard', active: activeSection === 'dashboard' },
    { id: 'practice', label: 'Practice', href: '#practice', active: activeSection === 'practice' },
    { id: 'lexicon', label: 'Lexicon', href: '#lexicon', active: activeSection === 'lexicon' },
    { id: 'settings', label: 'Settings', href: '#settings', active: activeSection === 'settings' },
  ];
  export let onBack: () => void = () => {};
  export let onSettings: () => void = () => {};
  export let onAdmin: () => void = () => {};
  export let onLogout: () => void = () => {};
  export let showAdmin = false;

  let state: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let error = '';
  let payload: PracticeAnalyticsResponse | null = null;
  let progressPayload: PracticeProgressResponse | null = null;
  let page = 1;
  const pageSize = 40;
  const activeDeckLimit = 10;

  const n = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? v : 0);
  const pct = (v: unknown) => (typeof v === 'number' && Number.isFinite(v) ? `${Math.round(v * 100)}%` : '0%');
  const obj = (v: unknown) => (v && typeof v === 'object' ? (v as Record<string, unknown>) : {});
  const rows = (v: unknown) => (Array.isArray(v) ? v : []);

  const pairLabel = (row: unknown) => {
    const r = obj(row);
    const prompt = String(r.prompt ?? '').trim();
    const answer = String(r.answer ?? '').trim();
    if (prompt || answer) return `${prompt || '?'} → ${answer || '?'}`;
    // Fallback: derive label from card_id / base_card_id
    const id = String(r.card_id ?? r.base_card_id ?? r.id ?? '');
    // Format: "word:the-students-are-bad#mirad-to-english" or "phrase:hello-world#english-to-mirad"
    const base = id.includes('#') ? id.split('#')[0] : id;
    // Strip type prefix ("word:", "phrase:") and convert hyphens to spaces
    const slug = base.replace(/^(word|phrase|card):/i, '').replace(/-/g, ' ').trim();
    return slug || '?';
  };

  const directionLabel = (row: unknown) => {
    const r = obj(row);
    const dir = String(r.direction ?? '').toLowerCase();
    if (dir === 'english-to-mirad' || dir === 'english_to_mirad') return 'en→mir';
    if (dir === 'mirad-to-english' || dir === 'mirad_to_english') return 'mir→en';
    return dir || '→';
  };

  const cardType = (row: unknown) => {
    const r = obj(row);
    const explicit = String(r.type ?? r.card_type ?? '').toLowerCase();
    if (explicit === 'word' || explicit === 'phrase') return explicit;
    const id = String(r.base_card_id ?? r.id ?? r.card_id ?? '').toLowerCase();
    if (id.startsWith('word:')) return 'word';
    if (id.startsWith('phrase:')) return 'phrase';
    return 'unknown';
  };

  const directionTheme = (row: unknown) => {
    const dir = directionLabel(row);
    if (dir === 'en→mir') return 'bg-blue-100 text-blue-800 ring-blue-200 dark:bg-blue-900/40 dark:text-blue-200 dark:ring-blue-800';
    if (dir === 'mir→en') return 'bg-violet-100 text-violet-800 ring-violet-200 dark:bg-violet-900/40 dark:text-violet-200 dark:ring-violet-800';
    return 'bg-slate-100 text-slate-700 ring-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:ring-slate-700';
  };

  const accuracyValue = (row: unknown) => {
    const r = obj(row);
    const explicit = r.accuracy;
    if (typeof explicit === 'number' && Number.isFinite(explicit)) return Math.max(0, Math.min(1, explicit));
    const attempts = n(r.attempts);
    if (attempts <= 0) return 0;
    return Math.max(0, Math.min(1, n(r.correct) / attempts));
  };

  const accuracyHeat = (row: unknown) => {
    const score = accuracyValue(row);
    if (score >= 0.85) return { badge: 'bg-emerald-100 text-emerald-800 ring-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-200 dark:ring-emerald-800', bar: 'bg-emerald-500' };
    if (score >= 0.6) return { badge: 'bg-amber-100 text-amber-800 ring-amber-200 dark:bg-amber-900/40 dark:text-amber-200 dark:ring-amber-800', bar: 'bg-amber-500' };
    return { badge: 'bg-rose-100 text-rose-800 ring-rose-200 dark:bg-rose-900/40 dark:text-rose-200 dark:ring-rose-800', bar: 'bg-rose-500' };
  };

  const cardTypeTheme = (row: unknown) => {
    const type = cardType(row);
    if (type === 'word') return { chip: 'bg-cyan-100 text-cyan-800 ring-cyan-200 dark:bg-cyan-900/40 dark:text-cyan-200 dark:ring-cyan-800', accent: 'border-cyan-200/80 bg-cyan-50/60 dark:border-cyan-900 dark:bg-cyan-950/30', dot: 'bg-cyan-500' };
    if (type === 'phrase') return { chip: 'bg-fuchsia-100 text-fuchsia-800 ring-fuchsia-200 dark:bg-fuchsia-900/40 dark:text-fuchsia-200 dark:ring-fuchsia-800', accent: 'border-fuchsia-200/80 bg-fuchsia-50/60 dark:border-fuchsia-900 dark:bg-fuchsia-950/30', dot: 'bg-fuchsia-500' };
    return { chip: 'bg-slate-100 text-slate-700 ring-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:ring-slate-700', accent: 'border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900/40', dot: 'bg-slate-500' };
  };

  const buildPerDirectionRows = (analytics: unknown[], progress: unknown[]) => {
    const progressByItemId = new Map<string, Record<string, unknown>>();
    for (const row of progress) {
      const r = obj(row);
      const itemId = String(r.id ?? r.card_id ?? '');
      if (itemId) progressByItemId.set(itemId, r);
    }
    const seen = new Map<string, Record<string, unknown>>();
    for (const row of analytics) {
      const r = obj(row);
      const key = String(r.card_id ?? r.id ?? '');
      if (!key) continue;
      // Enrich with prompt/answer from progress data
      const progressRow = progressByItemId.get(key) ?? {};
      const enriched = {
        ...r,
        prompt: String(r.prompt ?? progressRow.prompt ?? '').trim(),
        answer: String(r.answer ?? progressRow.answer ?? '').trim(),
        direction: String(r.direction ?? progressRow.direction ?? ''),
        type: r.type ?? r.card_type ?? progressRow.type ?? '',
        state: r.state ?? r.lifecycle ?? progressRow.state ?? 'new',
        mastery: r.mastery ?? progressRow.mastery,
        consecutive_correct: r.consecutive_correct ?? progressRow.mastery?.consecutive_correct ?? 0,
      };
      const existing = seen.get(key);
      if (!existing) {
        seen.set(key, enriched);
      } else {
        existing.attempts = n(existing.attempts) + n(r.attempts ?? r.seen);
        existing.correct = n(existing.correct) + n(r.correct);
        existing.incorrect = n(existing.incorrect) + n(r.incorrect ?? 0);
      }
    }
    // Add progress items not seen in analytics (unseen cards)
    for (const row of progress) {
      const r = obj(row);
      const key = String(r.id ?? r.card_id ?? '');
      if (!key || seen.has(key)) continue;
      seen.set(key, {
        ...r,
        attempts: 0,
        correct: 0,
        incorrect: 0,
        consecutive_correct: r.mastery?.consecutive_correct ?? 0,
      });
    }
    return Array.from(seen.values()).sort((a, b) => {
      const aDir = directionLabel(a);
      const bDir = directionLabel(b);
      if (aDir !== bDir) return aDir.localeCompare(bDir);
      return pairLabel(a).localeCompare(pairLabel(b));
    });
  };

  $: timing = obj(payload?.timing);
  $: streak = obj(payload?.streak);
  $: lifecycle = obj(payload?.lifecycle);
  $: direction = obj(payload?.direction_breakdown);
  $: cardTypes = obj(payload?.card_type_breakdown);
  $: masteredRecentRaw = obj(payload?.mastered_recent);
  $: analyticsPerCardRaw = payload?.per_card;
  $: analyticsPerCard = Array.isArray(analyticsPerCardRaw)
    ? analyticsPerCardRaw
    : Object.values(obj(analyticsPerCardRaw));
  $: progressPerCard = rows(progressPayload?.per_card);
  $: progressPerCard = rows(progressPayload?.per_card);
  const isRowMastered = (row: unknown) => {
    const r = obj(row);
    if (typeof r.is_mastered === 'boolean') return Boolean(r.is_mastered);
    const mastery = obj(r.mastery);
    if (typeof mastery.mastered === 'boolean') return Boolean(mastery.mastered);
    const state = String(r.state ?? r.lifecycle ?? '').toLowerCase();
    if (state === 'mastered' || state === 'revision' || state === 'stale') return true;

    const dir = String(r.direction ?? '').toLowerCase();
    const base = String(r.base_card_id ?? '');
    const recent = obj(masteredRecentRaw?.[base]);
    if (dir === 'english-to-mirad' || dir === 'english_to_mirad') {
      const e2m = obj(recent.english_to_mirad ?? recent['english-to-mirad']);
      return Boolean(e2m.all_correct);
    }
    if (dir === 'mirad-to-english' || dir === 'mirad_to_english') {
      const m2e = obj(recent.mirad_to_english ?? recent['mirad-to-english']);
      return Boolean(m2e.all_correct);
    }
    // Fallback: check the combined mastered flag from legacy analytics.
    if (typeof recent.mastered === 'boolean') return Boolean(recent.mastered);
    return false;
  };

  $: perDirectionRows = buildPerDirectionRows(analyticsPerCard, progressPerCard);
  $: masteredCards = perDirectionRows.filter((row) => isRowMastered(row));
  $: seenNotMasteredCards = perDirectionRows
    .filter((row) => {
      const r = obj(row);
      return n(r.attempts) > 0 && !isRowMastered(row);
    })
    .sort((a, b) => accuracyValue(b) - accuracyValue(a));
  $: activeDeckCount = Math.min(seenNotMasteredCards.length, n(payload?.active_deck_count ?? activeDeckLimit));
  $: activeDeckCards = seenNotMasteredCards.slice(0, activeDeckCount);
  $: allRows = [...masteredCards, ...activeDeckCards];
  $: totalRows = allRows.length;
  $: totalPages = Math.max(1, Math.ceil(totalRows / pageSize));
  $: page = Math.min(page, totalPages);
  $: start = (page - 1) * pageSize;
  $: end = start + pageSize;
  $: masteredPaged = masteredCards.slice(start, end);
  $: seenPaged = activeDeckCards.slice(Math.max(0, start - masteredCards.length), Math.max(0, end - masteredCards.length));
  $: sparseFlag = obj(payload?.sparse_history).is_sparse;
  $: sparseHistory = Boolean(sparseFlag) || (n(payload?.event_count) === 0 && n(payload?.session_count) === 0 && n(payload?.lifecycle_count) === 0);

  async function loadAnalytics() {
    state = payload ? 'ready' : 'loading';
    error = '';
    try {
      const [analyticsResult, progressResult] = await Promise.all([
        getPracticeAnalytics(),
        getPracticeProgress(),
      ]);
      const { response, payload: next } = analyticsResult;
      const { response: progressResponse, payload: nextProgress } = progressResult;
      payload = next;
      progressPayload = progressResponse.ok && nextProgress.ok !== false ? nextProgress : null;
      page = 1;
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
  navItems={effectiveNavItems}
  {showAdmin}
  on:click={onBack}
  on:settings={onSettings}
  on:admin={onAdmin}
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
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Streak</p><p class="mt-3 text-3xl font-semibold">{n(streak.current_days)} {n(streak.current_days) === 1 ? 'day' : 'days'}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Lifecycles</p><p class="mt-3 text-3xl font-semibold">{n(payload?.lifecycle_count)}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">Mastered</p><p class="mt-3 text-3xl font-semibold text-emerald-600 dark:text-emerald-300">{n(payload?.mastered_count)}</p></AppCard>
    <AppCard><p class="text-xs uppercase tracking-[0.2em] text-slate-400">Active</p><p class="mt-3 text-3xl font-semibold">{activeDeckCount}</p></AppCard>
  </div>

  <AppCard className="mt-4 space-y-6 overflow-auto">
    <p class="text-sm font-semibold">Per-card breakdown</p>

    {#if masteredCards.length === 0 && seenNotMasteredCards.length === 0}
      <p class="text-sm text-slate-500 dark:text-slate-400">No analytics yet.</p>
    {:else}
      <section class="space-y-2">
        <h3 class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">Mastered ({n(payload?.mastered_count)})</h3>
        {#if masteredPaged.length === 0}
          {#if page === 1}
            <p class="text-sm text-slate-500 dark:text-slate-400">No mastered cards yet.</p>
          {/if}
        {:else}
          <div class="grid gap-3">
            {#each masteredPaged as row}
              {@const r = obj(row)}
              {@const theme = cardTypeTheme(row)}
              {@const heat = accuracyHeat(row)}
              {@const score = accuracyValue(row)}
              <article class={`min-w-0 overflow-hidden rounded-lg border p-3 shadow-sm transition ${theme.accent}`}>
                <div class="flex items-center justify-between gap-2">
                  <div class="flex min-w-0 items-center gap-2">
                    <span class={`h-2 w-2 shrink-0 rounded-full ${theme.dot}`}></span>
                    <p class="min-w-0 break-words text-sm font-semibold text-slate-900 dark:text-slate-100">{pairLabel(row)}</p>
                    <span class={`shrink-0 inline-flex rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] ring-1 ${theme.chip}`}>{cardType(row)}</span>
                    <span class={`shrink-0 inline-flex rounded-full px-1.5 py-0.5 text-[10px] font-semibold ring-1 ${directionTheme(row)}`}>{directionLabel(row)}</span>
                  </div>
                  <span class={`shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] ring-1 ${heat.badge}`}>{pct(score)}</span>
                </div>
                <div class="mt-2 h-1.5 w-full rounded-full bg-slate-200/80 dark:bg-slate-800/80"><div class={`h-1.5 rounded-full ${heat.bar}`} style={`width: ${Math.round(score * 100)}%`}></div></div>
                <dl class="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">Correct</dt><dd class="font-semibold text-slate-900 dark:text-slate-100">{n(r.correct)}/{n(r.attempts)}</dd></div>
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">Streak</dt><dd class="font-semibold text-slate-900 dark:text-slate-100">{n(r.consecutive_correct ?? r.mastery?.consecutive_correct ?? 0)}</dd></div>
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">State</dt><dd class="font-semibold text-emerald-700 dark:text-emerald-300">Mastered</dd></div>
                </dl>
              </article>
            {/each}
          </div>
        {/if}
      </section>

      <section class="space-y-2">
        <h3 class="text-xs font-semibold uppercase tracking-[0.2em] text-amber-600 dark:text-amber-400">Active ({activeDeckCount})</h3>
        {#if seenPaged.length === 0}
          {#if page === 1}
            <p class="text-sm text-slate-500 dark:text-slate-400">No in-progress cards yet.</p>
          {/if}
        {:else}
          <div class="grid gap-3">
            {#each seenPaged as row}
              {@const r = obj(row)}
              {@const theme = cardTypeTheme(row)}
              {@const heat = accuracyHeat(row)}
              {@const score = accuracyValue(row)}
              <article class={`min-w-0 overflow-hidden rounded-lg border p-3 shadow-sm transition ${theme.accent}`}>
                <div class="flex items-center justify-between gap-2">
                  <div class="flex min-w-0 items-center gap-2">
                    <span class={`h-2 w-2 shrink-0 rounded-full ${theme.dot}`}></span>
                    <p class="min-w-0 break-words text-sm font-semibold text-slate-900 dark:text-slate-100">{pairLabel(row)}</p>
                    <span class={`shrink-0 inline-flex rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] ring-1 ${theme.chip}`}>{cardType(row)}</span>
                    <span class={`shrink-0 inline-flex rounded-full px-1.5 py-0.5 text-[10px] font-semibold ring-1 ${directionTheme(row)}`}>{directionLabel(row)}</span>
                  </div>
                  <span class={`shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-[0.14em] ring-1 ${heat.badge}`}>{pct(score)}</span>
                </div>
                <div class="mt-2 h-1.5 w-full rounded-full bg-slate-200/80 dark:bg-slate-800/80"><div class={`h-1.5 rounded-full ${heat.bar}`} style={`width: ${Math.round(score * 100)}%`}></div></div>
                <dl class="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">Correct</dt><dd class="font-semibold text-slate-900 dark:text-slate-100">{n(r.correct)}/{n(r.attempts)}</dd></div>
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">Streak</dt><dd class="font-semibold text-slate-900 dark:text-slate-100">{n(r.consecutive_correct ?? r.mastery?.consecutive_correct ?? 0)}/{n(r.mastery?.streak_required ?? 3)}</dd></div>
                  <div class="rounded-md bg-white/70 px-2 py-1 dark:bg-slate-900/60"><dt class="text-slate-500 dark:text-slate-400">State</dt><dd class="font-semibold text-amber-700 dark:text-amber-300">{accuracyValue(row) >= 0.9 ? 'strong' : accuracyValue(row) >= 0.7 ? 'improving' : 'weak'}</dd></div>
                </dl>
              </article>
            {/each}
          </div>
        {/if}
      </section>

      {#if totalRows > pageSize}
        <div class="flex items-center justify-end gap-2 border-t border-slate-200 pt-3 text-xs dark:border-slate-700">
          <AppButton variant="secondary" className="min-h-8 px-2" on:click={() => (page = Math.max(1, page - 1))} disabled={page <= 1}>Prev</AppButton>
          <span class="text-slate-500 dark:text-slate-400">Page {page} / {totalPages}</span>
          <AppButton variant="secondary" className="min-h-8 px-2" on:click={() => (page = Math.min(totalPages, page + 1))} disabled={page >= totalPages}>Next</AppButton>
        </div>
      {/if}
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
