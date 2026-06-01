<script lang="ts">
  import AppCard from '../ui/AppCard.svelte';
  import TopBar from './TopBar.svelte';

  export let title = 'Practice';
  export let subtitle = 'Focused study mode';
  export let showBackButton = true;
  export let backLabel = 'Back to dashboard';
  export let userLabel = 'Study mode';
  export let avatarLabel = 'Guest';
</script>

<div class="min-h-screen bg-gradient-to-b from-violet-50 via-white to-white text-slate-900 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 dark:text-slate-50">
  <div class="mx-auto flex min-h-screen max-w-4xl flex-col">
    <TopBar {title} {subtitle} {showBackButton} {backLabel} {userLabel} {avatarLabel} on:click on:settings on:logout />

    <main class="flex flex-1 items-center justify-center px-4 py-8 sm:px-6 lg:px-8">
      <div class="w-full max-w-2xl">
        <slot name="status" />
        <AppCard className="mx-auto w-full space-y-6 rounded-[2rem] p-6 sm:p-8">
          <slot />
        </AppCard>
      </div>
    </main>
  </div>
</div>
