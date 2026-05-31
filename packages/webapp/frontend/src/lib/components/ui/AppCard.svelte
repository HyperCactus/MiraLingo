<script lang="ts">
  export let className = '';
</script>

<section class={`rounded-2xl border border-violet-100 bg-white p-6 shadow-sm dark:border-violet-900/60 dark:bg-slate-950 ${className}`}>
  <slot />
</section>
