<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import privacyMarkdown from '../content/privacy-policy.md?raw';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  type Block =
    | { type: 'h1'; text: string }
    | { type: 'h2'; text: string }
    | { type: 'p'; text: string }
    | { type: 'ul'; items: string[] };

  const dispatch = createEventDispatcher<{ back: void }>();

  function inlineText(value: string): string {
    return value.replace(/^_+|_+$/g, '').replace(/\*\*(.*?)\*\*/g, '$1');
  }

  function parsePolicy(markdown: string): Block[] {
    const blocks: Block[] = [];
    const lines = markdown.split('\n');
    let listItems: string[] = [];
    let paragraph: string[] = [];

    const flushParagraph = () => {
      if (paragraph.length) {
        blocks.push({ type: 'p', text: inlineText(paragraph.join(' ')) });
        paragraph = [];
      }
    };

    const flushList = () => {
      if (listItems.length) {
        blocks.push({ type: 'ul', items: listItems.map(inlineText) });
        listItems = [];
      }
    };

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) {
        flushParagraph();
        flushList();
        continue;
      }

      if (line.startsWith('# ')) {
        flushParagraph();
        flushList();
        blocks.push({ type: 'h1', text: line.slice(2) });
        continue;
      }

      if (line.startsWith('## ')) {
        flushParagraph();
        flushList();
        blocks.push({ type: 'h2', text: line.slice(3) });
        continue;
      }

      if (line.startsWith('- ')) {
        flushParagraph();
        listItems.push(line.slice(2));
        continue;
      }

      flushList();
      paragraph.push(line);
    }

    flushParagraph();
    flushList();
    return blocks;
  }

  const policyBlocks = parsePolicy(privacyMarkdown);
</script>

<div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50">
  <main class="mx-auto flex min-h-screen max-w-4xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between gap-4">
      <AppButton variant="ghost" className="shrink-0" on:click={() => dispatch('back')}>
        <span aria-hidden="true">←</span>
        <span>Back</span>
      </AppButton>
      <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-violet-600 text-sm font-bold text-white shadow-sm dark:bg-violet-400 dark:text-slate-950">
        ML
      </span>
    </div>

    <AppCard className="overflow-hidden p-0">
      <div class="bg-gradient-to-br from-violet-600 via-violet-500 to-fuchsia-500 px-6 py-8 text-white sm:px-8">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-violet-100">MiraLingo</p>
        <h1 class="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Privacy Policy</h1>
        <p class="mt-3 max-w-2xl text-sm leading-6 text-violet-50/90">
          Clear notes on account data, learning progress, settings, and how MiraLingo uses them.
        </p>
      </div>

      <article class="space-y-6 px-6 py-8 sm:px-8">
        {#each policyBlocks as block, index (`${block.type}-${index}`)}
          {#if block.type === 'h1'}
            <h2 class="sr-only">{block.text}</h2>
          {:else if block.type === 'h2'}
            <h2 class="pt-2 text-xl font-semibold text-slate-900 dark:text-slate-50">{block.text}</h2>
          {:else if block.type === 'p'}
            <p class="text-sm leading-7 text-slate-600 dark:text-slate-300">{block.text}</p>
          {:else if block.type === 'ul'}
            <ul class="space-y-3 text-sm leading-7 text-slate-600 dark:text-slate-300">
              {#each block.items as item (item)}
                <li class="rounded-2xl bg-violet-50/70 px-4 py-3 dark:bg-violet-950/40">{item}</li>
              {/each}
            </ul>
          {/if}
        {/each}
      </article>
    </AppCard>
  </main>
</div>
