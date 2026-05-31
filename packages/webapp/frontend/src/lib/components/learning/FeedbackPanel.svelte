<script lang="ts">
  import AudioButton from './AudioButton.svelte';

  export let revealedAnswer = '';
  export let submittedAnswer = '';
  export let correct = false;
  export let canPlayAudio = false;
  export let audioLoading = false;
  export let audioLabel = 'Hear Mirad answer';
  export let audioMessage = '';
</script>

<section class="space-y-4 rounded-3xl border border-violet-100 bg-violet-50/70 p-4 dark:border-violet-900/70 dark:bg-violet-950/40">
  <div class="flex flex-wrap items-center gap-2">
    <span class={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${correct ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'}`}>
      {correct ? 'Correct' : 'Show answer'}
    </span>
    {#if submittedAnswer}
      <span class="text-xs font-medium text-slate-500 dark:text-slate-400">You entered “{submittedAnswer}”</span>
    {/if}
  </div>

  <div class="space-y-1">
    <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">Correct answer</p>
    <p class="text-2xl font-semibold text-slate-900 dark:text-slate-50">{revealedAnswer}</p>
  </div>

  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <div class="min-w-0 text-sm text-slate-500 dark:text-slate-400">
      {#if audioMessage}
        <p>{audioMessage}</p>
      {:else}
        <p>Listen to the Mirad answer after it has been revealed.</p>
      {/if}
    </div>
    {#if canPlayAudio}
      <AudioButton disabled={audioLoading} loading={audioLoading} label={audioLabel} />
    {/if}
  </div>
</section>
