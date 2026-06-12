<script lang="ts">
  import AppCard from '../ui/AppCard.svelte';
  import BottomNav, { type NavItem } from './BottomNav.svelte';
  import TopBar from './TopBar.svelte';

  export let title = 'Dashboard';
  export let subtitle = 'Daily practice overview';
  export let showBackButton = false;
  export let backLabel = 'Back';
  export let userLabel = '';
  export let avatarLabel = 'Guest';
  export let showAdmin = false;
  export let navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', href: '#dashboard', active: true },
    { id: 'practice', label: 'Practice', href: '#practice' },
    { id: 'lexicon', label: 'Lexicon', href: '#lexicon' },
    { id: 'settings', label: 'Settings', href: '#settings' },
  ];
</script>

<div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50">
  <div class="mx-auto flex min-h-screen max-w-6xl flex-col">
    <TopBar {title} {subtitle} {showBackButton} {backLabel} {userLabel} {avatarLabel} {showAdmin} on:click on:settings on:admin on:logout />

    <main class="flex-1 px-4 py-6 sm:px-6 lg:px-8">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <section class="min-w-0">
          <slot name="hero" />
          <div class="mt-6">
            <slot />
          </div>
        </section>

        <aside class="space-y-4">
          <slot name="sidebar">
            <AppCard className="space-y-3">
              <div>
                <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Study snapshot</p>
                <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  AppShell reserves a secondary column for analytics, shortcuts, or account controls.
                </p>
              </div>
            </AppCard>
          </slot>
        </aside>
      </div>
    </main>

    <div class="sticky bottom-0 mt-auto">
      <BottomNav items={navItems} />
    </div>
  </div>
</div>
