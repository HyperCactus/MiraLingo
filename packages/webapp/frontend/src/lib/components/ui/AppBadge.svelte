<script lang="ts">
  export let tone: 'default' | 'success' | 'warning' | 'danger' = 'default';
  export let className = '';

  const toneClasses = {
    default: 'bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-200',
    success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
    danger: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200',
  };
</script>

<span class={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${toneClasses[tone]} ${className}`}>
  <slot />
</span>
