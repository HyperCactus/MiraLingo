<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppBadge from '../ui/AppBadge.svelte';
  import AppButton from '../ui/AppButton.svelte';

  const dispatch = createEventDispatcher<{ settings: void; logout: void }>();

  export let title = 'MiraLingo';
  export let subtitle = '';
  export let userLabel = '';
  export let showBackButton = false;
  export let backLabel = 'Back';
  export let avatarLabel = 'Guest';

  let menuOpen = false;

  function closeMenu() {
    menuOpen = false;
  }
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
            <p class="hidden truncate text-sm text-slate-500 dark:text-slate-400 sm:block">{subtitle}</p>
          {/if}
        </div>
      </div>
    </div>
  </div>

  <div class="flex shrink-0 items-center gap-3">
    {#if userLabel}
      <div class="hidden sm:block">
        <AppBadge>{userLabel}</AppBadge>
      </div>
    {/if}
    <div class="relative">
      <button
        type="button"
        class="flex h-10 w-10 items-center justify-center rounded-full border border-violet-200 bg-violet-50 text-sm font-semibold text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-200"
        aria-label={`Active user ${avatarLabel}`}
        title={avatarLabel}
        aria-haspopup="menu"
        aria-expanded={menuOpen}
        on:click={() => (menuOpen = !menuOpen)}
      >
        {avatarLabel.slice(0, 2).toUpperCase()}
      </button>

      {#if menuOpen}
        <!-- svelte-ignore a11y-interactive-supports-focus -->
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <div class="absolute right-0 z-20 mt-2 w-40 rounded-2xl border border-violet-100 bg-white p-2 shadow-lg dark:border-violet-900/60 dark:bg-slate-950" role="menu" tabindex="-1" on:click={() => (menuOpen = false)} on:keydown={(e) => e.key === 'Escape' && (menuOpen = false)}>
          <button type="button" class="w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-violet-50 dark:hover:bg-violet-950/40" role="menuitem" on:click={() => { menuOpen = false; dispatch('settings'); }}>
            Settings
          </button>
          <button type="button" class="w-full rounded-xl px-3 py-2 text-left text-sm text-red-700 hover:bg-red-50 dark:text-red-300 dark:hover:bg-red-950/30" role="menuitem" on:click={() => { menuOpen = false; dispatch('logout'); }}>
            Log out
          </button>
        </div>
      {/if}
    </div>
  </div>
</header>
