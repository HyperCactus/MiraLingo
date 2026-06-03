<script lang="ts">
  export let open = false;
  export let title = '';
  export let className = '';
</script>

{#if open}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 px-4 py-6">
    <div
      class={`w-full max-w-lg rounded-2xl border border-violet-100 bg-white p-6 shadow-2xl dark:border-violet-900 dark:bg-slate-950 ${className}`}
      role="dialog"
      aria-modal="true"
      aria-label={title || 'Dialog'}
      tabindex="-1"
    >
      {#if title}
        <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
      {/if}
      <slot />
    </div>
  </div>
{/if}
