<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';
  import { get } from 'svelte/store';
  import { fetchMbrolaTextAudio } from '../api/audio.ts';
  import { readJson } from '../api/auth.ts';
  import { LookupError, lookupWord, lookupExact, type LookupDirection, type LookupResult } from '../api/lookup.ts';
  import AppShell from '../components/layout/AppShell.svelte';
  import DirectionToggle from '../components/lexicon/DirectionToggle.svelte';
  import LexiconResultRow from '../components/lexicon/LexiconResultRow.svelte';
  import AppCard from '../components/ui/AppCard.svelte';
  import AppInput from '../components/ui/AppInput.svelte';
  import type { NavItem } from '../components/layout/BottomNav.svelte';
  import { ttsSpeed } from '../stores/settings.ts';

  const dispatch = createEventDispatcher<{
    back: void;
    settings: void;
    logout: void;
  }>();

  export let userName = 'Learner';
  export let navItems: NavItem[] = [
    { id: 'dashboard', label: 'Today', href: '#dashboard' },
    { id: 'practice', label: 'Practice', href: '#practice' },
    { id: 'lexicon', label: 'Lexicon', href: '#lexicon', active: true },
    { id: 'settings', label: 'Settings', href: '#settings' },
  ];

  let query = '';
  let direction: LookupDirection = 'en_to_mir';
  let state: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let results: LookupResult[] = [];
  let exactResult: LookupResult | null = null;   // shown immediately
  let error = '';
  let debounceTimer: ReturnType<typeof setTimeout> | null = null;
  let lookupToken = 0;
  let speakingWord = '';
  let audioFeedback = '';
  let activePreviewAudio: HTMLAudioElement | null = null;
  let activePreviewAudioUrl = '';

  const debounceMs = 300;

  $: normalizedQuery = query.trim();
  $: hasQuery = normalizedQuery.length > 0;
  $: placeholder = direction === 'en_to_mir' ? 'Search an English word' : 'Search a Mirad word';
  $: emptyPrompt = direction === 'en_to_mir'
    ? 'Type a word to find similar Mirad translations'
    : 'Type a word to find similar English translations';
  $: noResultsMessage = `No similar words found for '${normalizedQuery}'.`;
  $: showNoResults = state === 'ready' && hasQuery && results.length === 0 && !exactResult;
  $: audioAvailable = true;

  function clearPendingLookup() {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
      debounceTimer = null;
    }
  }

  function resetSearchSurface() {
    clearPendingLookup();
    lookupToken += 1;
    state = 'idle';
    results = [];
    exactResult = null;
    error = '';
  }

  function resetPreviewAudio() {
    if (activePreviewAudio) {
      activePreviewAudio.pause();
      activePreviewAudio = null;
    }
    if (activePreviewAudioUrl) {
      URL.revokeObjectURL(activePreviewAudioUrl);
      activePreviewAudioUrl = '';
    }
    speakingWord = '';
  }

  async function runLookup(expectedQuery: string, expectedDirection: LookupDirection) {
    const token = ++lookupToken;
    state = 'loading';
    error = '';
    audioFeedback = '';
    exactResult = null;
    results = [];

    // Fire both in parallel; track them independently so one can't overwrite the other
    const exactPromise = lookupExact(expectedQuery, expectedDirection);
    const semanticPromise = lookupWord(expectedQuery, expectedDirection);

    // Phase 1: exact match from SQLite — sub-10ms, no embedder needed
    const [exactHits] = await Promise.all([exactPromise]);
    if (token !== lookupToken) return;
    exactResult = exactHits[0] ?? null;

    // Phase 2: full semantic lookup (may take ~2s on first query)
    let semanticHits: LookupResult[] = [];
    try {
      semanticHits = await semanticPromise;
    } catch (cause) {
      if (token !== lookupToken) return;
      // No semantic — if we have exact, degrade gracefully; otherwise hard error
      if (!exactResult) {
        results = [];
        state = 'error';
        error = cause instanceof LookupError ? cause.detail || cause.message : 'Search unavailable right now — try again later';
        return;
      }
      // exact covers us; semantic is a soft failure
    }

    if (token !== lookupToken || expectedQuery !== normalizedQuery || expectedDirection !== direction) return;

    if (semanticHits.length > 0) {
      results = semanticHits;
    } else if (exactResult) {
      // Semantic found nothing but we have exact — still a valid result
      results = [];
    }
    state = 'ready';
  }

  function scheduleLookup() {
    clearPendingLookup();

    if (!hasQuery) {
      state = 'idle';
      results = [];
      error = '';
      audioFeedback = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      void runLookup(normalizedQuery, direction);
    }, debounceMs);
  }

  function getMiradWord(result: LookupResult) {
    return result.mirad;
  }

  function getPreviewMiradText(result: LookupResult): string {
    const raw = getMiradWord(result).trim();
    if (!raw) return '';

    return raw
      .replace(/[()\[\]{}"“”]/g, '')
      .replace(/\s*,\s*/g, ', ')
      .replace(/\s*;\s*/g, '; ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  async function playMbrolaPreview(text: string, spokenWord: string) {
    const response = await fetchMbrolaTextAudio(text);
    const contentType = response.headers.get('content-type') ?? '';

    if (!response.ok || !contentType.includes('audio')) {
      const payload = await readJson<{ detail?: string; error?: string }>(response);
      const detail = payload?.detail?.trim?.() || payload?.error?.trim?.() || 'Speech preview is unavailable for this result.';
      throw new Error(detail);
    }

    const blob = await response.blob();
    const nextUrl = URL.createObjectURL(blob);
    const nextAudio = new Audio(nextUrl);
    const configuredSpeed = Number(get(ttsSpeed));
    nextAudio.playbackRate = Number.isFinite(configuredSpeed) && configuredSpeed > 0 ? configuredSpeed : 0.8;
    nextAudio.onended = () => {
      if (speakingWord === spokenWord) {
        speakingWord = '';
      }
    };
    nextAudio.onerror = () => {
      if (speakingWord === spokenWord) {
        speakingWord = '';
      }
      audioFeedback = 'Speech preview could not play right now.';
    };

    resetPreviewAudio();
    activePreviewAudio = nextAudio;
    activePreviewAudioUrl = nextUrl;
    await nextAudio.play();
  }

  async function speakResult(result: LookupResult) {
    audioFeedback = '';
    const miradWord = getMiradWord(result).trim();
    const previewText = getPreviewMiradText(result);

    if (!previewText) {
      audioFeedback = 'Speech preview is unavailable for this result.';
      return;
    }

    speakingWord = miradWord || previewText;

    try {
      await playMbrolaPreview(previewText, speakingWord);
    } catch (error) {
      speakingWord = '';
      const detail = error instanceof Error ? error.message.trim() : '';
      audioFeedback = detail || 'Speech preview could not play right now.';
    }
  }

  $: if (normalizedQuery || direction) {
    scheduleLookup();
  }

  onDestroy(() => {
    clearPendingLookup();
    lookupToken += 1;
    resetPreviewAudio();
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  });
</script>

<AppShell
  title="Lexicon"
  subtitle="Search English and Mirad vocabulary with similarity hints"
  showBackButton={true}
  backLabel="Back to today"
  userLabel={state === 'loading' ? 'Searching' : 'Lookup'}
  avatarLabel={userName}
  {navItems}
  on:click={() => dispatch('back')}
  on:settings={() => dispatch('settings')}
  on:logout={() => dispatch('logout')}
>
  <svelte:fragment slot="hero">
    <AppCard className="space-y-5 bg-gradient-to-br from-violet-600 via-violet-500 to-fuchsia-500 text-white shadow-lg">
      <div class="space-y-2">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-violet-100">Lexicon search</p>
        <h1 class="text-3xl font-semibold leading-tight sm:text-4xl">Find similar words in either direction.</h1>
        <p class="max-w-2xl text-sm leading-6 text-violet-50/90 sm:text-base">
          Search English or Mirad words and find close matches while you study.
        </p>
      </div>

      <div class="grid gap-4 lg:grid-cols-[minmax(0,1.4fr)_auto] lg:items-end">
        <AppInput
          id="lexicon-search"
          label="Search"
          type="search"
          bind:value={query}
          placeholder={placeholder}
          autocomplete="off"
          className="text-white"
        />
        <DirectionToggle bind:value={direction} disabled={state === 'loading' && !hasQuery} />
      </div>
    </AppCard>
  </svelte:fragment>

  <div class="space-y-4">
    {#if state === 'error'}
      <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
        <p role="alert">Search unavailable right now — try again later</p>
      </AppCard>
    {:else if !hasQuery}
      <AppCard>
        <p class="text-lg font-semibold text-slate-900 dark:text-slate-100">Start a lookup</p>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{emptyPrompt}</p>
      </AppCard>
    {:else if state === 'loading'}
      {#if exactResult}
        <!-- Show exact match immediately while semantic results load -->
        <div class="space-y-2">
          <p class="px-1 text-xs font-semibold uppercase tracking-wider text-violet-600 dark:text-violet-400">Exact match</p>
          <LexiconResultRow
            result={exactResult}
            {direction}
            speaking={speakingWord === exactResult.mirad}
            {audioAvailable}
            on:speak={() => speakResult(exactResult)}
          />
          {#if results.length === 0}
            <!-- No semantic results yet — show skeleton for "similar" section -->
            <div class="mt-3 space-y-2">
              <p class="px-1 text-xs font-medium text-slate-400 dark:text-slate-500">Similar words — searching…</p>
              <AppCard className="animate-pulse space-y-3 p-4">
                <div class="h-4 w-20 rounded bg-slate-200 dark:bg-slate-700"></div>
                <div class="h-6 w-2/5 rounded bg-slate-200 dark:bg-slate-700"></div>
                <div class="h-16 rounded-xl bg-violet-100/60 dark:bg-violet-950/30"></div>
              </AppCard>
            </div>
          {:else}
            <!-- Semantic results arrived — show similar section -->
            <div class="mt-3 space-y-2">
              <p class="px-1 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Similar words</p>
              {#each results.filter(r => !r.is_exact) as result, index (`${direction}-${result.english}-${result.mirad}-sim-${index}`)}
                <LexiconResultRow
                  {result}
                  {direction}
                  speaking={speakingWord === result.mirad}
                  {audioAvailable}
                  on:speak={() => speakResult(result)}
                />
              {/each}
            </div>
          {/if}
        </div>
      {:else}
        <!-- No exact match yet, show loading skeletons -->
        <div class="space-y-3" aria-live="polite" aria-busy="true">
          <AppCard className="animate-pulse space-y-3 p-5">
            <div class="h-4 w-24 rounded bg-slate-200 dark:bg-slate-800"></div>
            <div class="h-8 w-2/5 rounded bg-slate-200 dark:bg-slate-800"></div>
            <div class="h-20 rounded-2xl bg-violet-100/70 dark:bg-violet-950/40"></div>
          </AppCard>
          <AppCard className="animate-pulse space-y-3 p-5">
            <div class="h-4 w-24 rounded bg-slate-200 dark:bg-slate-800"></div>
            <div class="h-8 w-1/3 rounded bg-slate-200 dark:bg-slate-800"></div>
            <div class="h-20 rounded-2xl bg-violet-100/70 dark:bg-violet-950/40"></div>
          </AppCard>
        </div>
      {/if}
    {:else if showNoResults}
      <AppCard>
        <p class="text-lg font-semibold text-slate-900 dark:text-slate-100">No results yet</p>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{noResultsMessage}</p>
      </AppCard>
    {:else}
      <!-- state === 'ready' — show all results (exact already included in results from backend) -->
      <div class="space-y-2">
        {#each results as result, index (`${direction}-${result.english}-${result.mirad}-${index}`)}
          <LexiconResultRow
            {result}
            {direction}
            speaking={speakingWord === result.mirad}
            {audioAvailable}
            on:speak={() => speakResult(result)}
          />
        {/each}
      </div>
    {/if}

    {#if audioFeedback}
      <AppCard className="border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
        <p>{audioFeedback}</p>
      </AppCard>
    {/if}
  </div>

  <svelte:fragment slot="sidebar">
    <AppCard className="space-y-3">
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Search tips</p>
      <ul class="space-y-3 text-sm leading-6 text-slate-500 dark:text-slate-400">
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Type one word at a time for best results.</li>
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Switch direction to search from Mirad back to English.</li>
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Use audio preview to hear Mirad words.</li>
      </ul>
    </AppCard>

    <AppCard className="space-y-2">
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Current direction</p>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        {direction === 'en_to_mir' ? 'English source → Mirad translation' : 'Mirad source → English translation'}
      </p>
    </AppCard>
  </svelte:fragment>
</AppShell>
