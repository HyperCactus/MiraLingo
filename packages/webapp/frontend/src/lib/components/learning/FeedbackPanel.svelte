<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AudioButton from './AudioButton.svelte';
  import ClickableTranslationText from './ClickableTranslationText.svelte';

  const dispatch = createEventDispatcher<{
    audio: void;
    lookup: { word: string; language: 'english' | 'mirad'; anchorRect: DOMRect };
  }>();

  export let revealedAnswer = '';
  export let submittedAnswer = '';
  export let correct = false;
  export let canPlayAudio = false;
  export let audioLoading = false;
  export let audioPlaying = false;
  export let audioLabel = 'Play Mirad audio';
  export let audioMessage = '';
  export let answerLanguage: 'english' | 'mirad' = 'mirad';
</script>

<section class="space-y-4 rounded-3xl border border-violet-100 bg-violet-50/70 p-4 dark:border-violet-900/70 dark:bg-violet-950/40">
  <div class="flex flex-wrap items-center gap-2">
    <span class={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${correct ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'}`}>
      {correct ? 'Correct' : 'Answer revealed'}
    </span>
    {#if submittedAnswer}
      <span class="text-xs font-medium text-slate-500 dark:text-slate-400">You entered “{submittedAnswer}”</span>
    {/if}
  </div>

  <div class="space-y-1">
    <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">Correct answer</p>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <ClickableTranslationText
        text={revealedAnswer}
        language={answerLanguage}
        className="text-2xl font-semibold text-slate-900 dark:text-slate-50"
        on:lookup={(event) => dispatch('lookup', event.detail)}
      />
      {#if canPlayAudio && answerLanguage === 'mirad'}
        <AudioButton disabled={audioLoading} loading={audioLoading} playing={audioPlaying} label={audioPlaying ? 'Stop Mirad audio' : audioLabel} on:click={() => dispatch('audio')} />
      {/if}
    </div>
  </div>

  {#if audioMessage}
    <p class="text-sm text-slate-500 dark:text-slate-400">{audioMessage}</p>
  {/if}
</section>
