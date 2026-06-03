<script lang="ts">
  import type { LookupResult } from '../../api/lookup';

  export let results: LookupResult[] = [];
  export let visible = false;
  export let anchorRect: DOMRect | null = null;
  export let direction: 'en_to_mir' | 'mir_to_en' = 'en_to_mir';
  export let loading = false;
  export let error = '';

  $: position = (() => {
    if (!anchorRect) return { top: 0, left: 0 };
    const gap = 6;
    const bubbleWidth = 180;
    // Position above the word
    const top = anchorRect.top - gap;
    // Clamp horizontally to viewport
    const maxLeft = window.innerWidth - bubbleWidth - 8;
    const left = Math.max(8, Math.min(anchorRect.left, maxLeft));
    return { top, left };
  })();

  $: translations = results.map(r => direction === 'en_to_mir' ? r.mirad : r.english);

  function close() {
    visible = false;
  }
</script>

{#if visible}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="fixed inset-0 z-40" on:click={close} on:keydown={close}></div>
  <div
    class="fixed z-50 rounded-lg border border-violet-200 bg-white px-3 py-2 shadow-lg dark:border-violet-800 dark:bg-slate-900"
    style="top: {position.top}px; left: {position.left}px; transform: translateY(-100%);"
    on:click|stopPropagation
  >
    {#if loading}
      <div class="flex items-center gap-2 text-xs text-slate-400">
        <div class="h-3 w-3 animate-spin rounded-full border-2 border-violet-400 border-t-transparent"></div>
        Looking up…
      </div>
    {:else if error}
      <p class="text-xs text-red-500">{error}</p>
    {:else if results.length === 0}
      <p class="text-xs text-slate-400">No translation found</p>
    {:else}
      <div class="flex flex-wrap items-baseline gap-x-1.5">
        {#each translations as word, i}
          <span class="text-sm font-semibold text-violet-600 dark:text-violet-400{results[i]?.is_exact ? '' : ' opacity-75'}">{word}</span>
          {#if i < translations.length - 1}
            <span class="text-slate-300 dark:text-slate-600">·</span>
          {/if}
        {/each}
      </div>
    {/if}
  </div>
{/if}