<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher<{
    lookup: { word: string; language: 'english' | 'mirad'; anchorRect: DOMRect };
  }>();

  export let text = '';
  export let language: 'english' | 'mirad' = 'english';
  export let className = '';

  function tokenize(value: string): Array<{ token: string; isWord: boolean }> {
    return value.split(/(\s+)/).map((part) => ({
      token: part,
      isWord: /[A-Za-zÀ-ÖØ-öø-ÿ]/.test(part),
    }));
  }

  function normalizeWord(token: string): string {
    return token.replace(/^[^A-Za-zÀ-ÖØ-öø-ÿ']+|[^A-Za-zÀ-ÖØ-öø-ÿ']+$/g, '').trim();
  }

  function onWordClick(event: MouseEvent, token: string) {
    const word = normalizeWord(token);
    if (!word) return;
    const target = event.currentTarget as HTMLElement;
    dispatch('lookup', { word, language, anchorRect: target.getBoundingClientRect() });
  }
</script>

<p class={className}>
  {#each tokenize(text) as part}
    {#if part.isWord}
      <button
        type="button"
        data-word-click-target
        class="inline rounded px-0.5 underline decoration-dotted underline-offset-4 hover:bg-violet-100 dark:hover:bg-violet-900/50"
        on:click={(event) => onWordClick(event, part.token)}
      >{part.token}</button>
    {:else}
      <span>{part.token}</span>
    {/if}
  {/each}
</p>
