<script lang="ts">
  import AppBadge from '../ui/AppBadge.svelte';
  import AppButton from '../ui/AppButton.svelte';

  export let title = 'MiraLingo';
  export let subtitle = '';
  export let userLabel = '';
  export let showBackButton = false;
  export let backLabel = 'Back';
  export let avatarLabel = 'Guest';
</script>

<header class="flex items-center justify-between gap-4 border-b border-violet-100 px-4 py-4 dark:border-violet-900/60 sm:px-6">
  <div class="flex min-w-0 items-center gap-3">
    {#if showBackButton}
      <AppButton variant="ghost" className="shrink-0" on:click>
        <span aria-hidden="true">←</span>
        <span>{backLabel}</span>
      </AppButton>
    {/if}

    <div class="min-w-0">
      <div class="flex items-center gap-2">
        <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-violet-600 text-sm font-bold text-white shadow-sm dark:bg-violet-400 dark:text-slate-950">
          ML
        </span>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold uppercase tracking-[0.2em] text-violet-600 dark:text-violet-300">
            {title}
          </p>
          {#if subtitle}
            <p class="truncate text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <div class="flex shrink-0 items-center gap-3">
    {#if userLabel}
      <AppBadge>{userLabel}</AppBadge>
    {/if}
    <div
      class="flex h-10 w-10 items-center justify-center rounded-full border border-violet-200 bg-violet-50 text-sm font-semibold text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-200"
      aria-label={`Active user ${avatarLabel}`}
      title={avatarLabel}
    >
      {avatarLabel.slice(0, 2).toUpperCase()}
    </div>
  </div>
</header>
