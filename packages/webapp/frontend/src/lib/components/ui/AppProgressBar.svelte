<script lang="ts">
  export let value = 0;
  export let max = 100;
  export let showLabel = false;
  export let className = '';

  $: percent = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
</script>

<div class={`flex flex-col gap-2 ${className}`}>
  {#if showLabel}
    <div class="flex items-center justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
      <span>Progress</span>
      <span>{Math.round(percent)}%</span>
    </div>
  {/if}
  <div class="h-2.5 overflow-hidden rounded-full bg-violet-100 dark:bg-violet-950" role="progressbar" aria-valuemin="0" aria-valuemax={max} aria-valuenow={value}>
    <div class="h-full rounded-full bg-violet-600 transition-[width] duration-300 dark:bg-violet-400" style={`width: ${percent}%`}></div>
  </div>
</div>
