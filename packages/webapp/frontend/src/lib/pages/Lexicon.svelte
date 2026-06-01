<script lang="ts">
  import { createEventDispatcher, onDestroy } from 'svelte';
  import { get } from 'svelte/store';
  import { fetchMbrolaTextAudio } from '../api/audio.ts';
  import { LookupError, lookupWord, type LookupDirection, type LookupResult } from '../api/lookup.ts';
  import AppShell from '../components/layout/AppShell.svelte';
  import DirectionToggle from '../components/lexicon/DirectionToggle.svelte';
  import LexiconResultRow from '../components/lexicon/LexiconResultRow.svelte';
  import AppCard from '../components/ui/AppCard.svelte';
  import AppInput from '../components/ui/AppInput.svelte';
  import type { NavItem } from '../components/layout/BottomNav.svelte';
  import { ttsSpeed } from '../stores/settings.ts';

  const dispatch = createEventDispatcher<{
    back: void;
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
  $: showNoResults = state === 'ready' && hasQuery && results.length === 0;
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

    try {
      const nextResults = await lookupWord(expectedQuery, expectedDirection);
      if (token !== lookupToken || expectedQuery !== normalizedQuery || expectedDirection !== direction) {
        return;
      }
      results = nextResults;
      state = 'ready';
    } catch (cause) {
      if (token !== lookupToken) {
        return;
      }
      results = [];
      state = 'error';
      error = cause instanceof LookupError ? cause.detail || cause.message : 'Search unavailable right now — try again later';
    }
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
    return direction === 'en_to_mir' ? result.mirad : result.mirad;
  }

  async function playMbrolaPreview(text: string, spokenWord: string) {
    const response = await fetchMbrolaTextAudio(text);
    const contentType = response.headers.get('content-type') ?? '';

    if (!response.ok || !contentType.includes('audio')) {
      throw new Error('practice-audio-unavailable');
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

    if (!miradWord) {
      audioFeedback = 'Speech preview is unavailable for this result.';
      return;
    }

    speakingWord = miradWord;

    try {
      await playMbrolaPreview(miradWord, miradWord);
    } catch (_) {
      speakingWord = '';
      audioFeedback = 'MBROLA preview is unavailable for this result right now.';
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
>
  <svelte:fragment slot="hero">
    <AppCard className="space-y-5 bg-gradient-to-br from-violet-600 via-violet-500 to-fuchsia-500 text-white shadow-lg">
      <div class="space-y-2">
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-violet-100">Lexicon search</p>
        <h1 class="text-3xl font-semibold leading-tight sm:text-4xl">Find similar words in either direction.</h1>
        <p class="max-w-2xl text-sm leading-6 text-violet-50/90 sm:text-base">
          Search from English into Mirad or reverse the lookup to inspect likely English matches, then skim exactness and cosine similarity without leaving AppShell.
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
    {:else if showNoResults}
      <AppCard>
        <p class="text-lg font-semibold text-slate-900 dark:text-slate-100">No results yet</p>
        <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{noResultsMessage}</p>
      </AppCard>
    {:else}
      <div class="space-y-3" aria-live="polite">
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
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">How lookup works</p>
      <ul class="space-y-3 text-sm leading-6 text-slate-500 dark:text-slate-400">
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Search waits 300ms after typing before it calls <code>/lookup</code>.</li>
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Similarity badges show cosine distance ranking from the semantic search backend.</li>
        <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">Audio preview uses authenticated MBROLA synthesis for the displayed Mirad text.</li>
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
