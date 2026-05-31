<script lang="ts">
  export let eyebrow = 'Prompt';
  export let text = '';
  export let supportingText = '';
</script>

<div class="space-y-3 text-center sm:text-left">
  <p class="text-xs font-semibold uppercase tracking-[0.28em] text-violet-500 dark:text-violet-300">{eyebrow}</p>
  <h2 class="text-balance text-3xl font-semibold leading-tight text-slate-900 dark:text-slate-50 sm:text-4xl">
    {text}
  </h2>
  {#if supportingText}
    <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">{supportingText}</p>
  {/if}
</div>
