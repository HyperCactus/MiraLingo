<script lang="ts">
  export let visible = false;
  export let tone: 'info' | 'success' | 'warning' | 'error' = 'info';
  export let className = '';

  const toneClasses = {
    info: 'border-violet-200 bg-white text-slate-800 dark:border-violet-900 dark:bg-slate-950 dark:text-slate-100',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-100',
    warning: 'border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900 dark:bg-amber-950/80 dark:text-amber-100',
    error: 'border-red-200 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950/80 dark:text-red-100',
  };
</script>

{#if visible}
  <div class={`pointer-events-none fixed right-4 top-4 z-50 max-w-sm rounded-xl border px-4 py-3 shadow-lg ${toneClasses[tone]} ${className}`} role="status" aria-live="polite">
    <slot />
  </div>
{/if}
