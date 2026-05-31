<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { LookupDirection, LookupResult } from '../../api/lookup.ts';
  import AudioButton from '../learning/AudioButton.svelte';
  import AppBadge from '../ui/AppBadge.svelte';
  import AppCard from '../ui/AppCard.svelte';

  const dispatch = createEventDispatcher<{
    speak: { text: string };
  }>();

  export let result: LookupResult;
  export let direction: LookupDirection = 'en_to_mir';
  export let speaking = false;
  export let audioAvailable = true;

  $: sourceWord = direction === 'en_to_mir' ? result.english : result.mirad;
  $: translationWord = direction === 'en_to_mir' ? result.mirad : result.english;
  $: sourceLabel = direction === 'en_to_mir' ? 'Source word' : 'Mirad word';
  $: translationLabel = direction === 'en_to_mir' ? 'Mirad translation' : 'English translation';
  $: similarityLabel = `${Math.round(result.cosine_similarity * 100)}% similarity`;
</script>

<AppCard className="space-y-4 p-4 sm:p-5">
  <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <div class="min-w-0 space-y-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">{sourceLabel}</p>
        <p class="mt-2 break-words text-2xl font-semibold text-slate-900 dark:text-slate-50">{sourceWord}</p>
      </div>

      <div class="rounded-2xl border border-violet-100 bg-violet-50/70 px-4 py-3 dark:border-violet-900/60 dark:bg-violet-950/30">
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-violet-700 dark:text-violet-300">{translationLabel}</p>
        <p class="mt-2 break-words text-lg font-semibold text-slate-900 dark:text-slate-50">{translationWord}</p>
      </div>
    </div>

    <div class="flex shrink-0 flex-col items-stretch gap-3 sm:items-end">
      <div class="flex flex-wrap justify-end gap-2">
        <AppBadge>{similarityLabel}</AppBadge>
        {#if result.is_exact}
          <AppBadge tone="success">Exact</AppBadge>
        {/if}
      </div>

      <AudioButton
        disabled={!audioAvailable || !translationWord}
        loading={speaking}
        label={speaking ? 'Speaking…' : 'Hear translation'}
        on:click={() => dispatch('speak', { text: translationWord })}
      />
    </div>
  </div>

  <dl class="grid gap-3 text-sm text-slate-500 dark:text-slate-400 sm:grid-cols-2">
    <div class="rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-900/60">
      <dt class="font-semibold text-slate-900 dark:text-slate-100">Similarity score</dt>
      <dd class="mt-1">{result.cosine_similarity.toFixed(3)}</dd>
    </div>
    <div class="rounded-2xl bg-slate-50 px-3 py-3 dark:bg-slate-900/60">
      <dt class="font-semibold text-slate-900 dark:text-slate-100">Match type</dt>
      <dd class="mt-1">{result.is_exact ? 'Exact lexical match' : 'Semantic neighbor'}</dd>
    </div>
  </dl>
</AppCard>
