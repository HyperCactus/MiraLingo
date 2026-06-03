<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import ClickableTranslationText from './ClickableTranslationText.svelte';
  import AudioButton from './AudioButton.svelte';

  const dispatch = createEventDispatcher<{
    lookup: { word: string; language: 'english' | 'mirad'; anchorRect: DOMRect };
    audio: void;
  }>();

  export let eyebrow = 'Prompt';
  export let text = '';
  export let supportingText = '';
  export let language: 'english' | 'mirad' = 'english';
  export let canPlayAudio = false;
  export let audioLoading = false;
</script>

<div class="space-y-3 text-center sm:text-left">
  <p class="text-xs font-semibold uppercase tracking-[0.28em] text-violet-500 dark:text-violet-300">{eyebrow}</p>
  <div class="flex items-start justify-center gap-3 sm:justify-between">
    <h2 class="text-balance text-3xl font-semibold leading-tight text-slate-900 dark:text-slate-50 sm:text-4xl">
      <ClickableTranslationText
        text={text}
        {language}
        className="inline"
        on:lookup={(event) => dispatch('lookup', event.detail)}
      />
    </h2>
    {#if canPlayAudio}
      <div class="shrink-0 pt-1">
        <AudioButton disabled={audioLoading} loading={audioLoading} label="Play Mirad audio" on:click={() => dispatch('audio')} />
      </div>
    {/if}
  </div>
  {#if supportingText}
    <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">{supportingText}</p>
  {/if}
</div>
