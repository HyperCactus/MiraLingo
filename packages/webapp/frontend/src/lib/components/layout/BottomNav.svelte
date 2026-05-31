<script lang="ts">
  export type NavItem = {
    id: string;
    label: string;
    href?: string;
    active?: boolean;
  };

  export let items: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', href: '#dashboard', active: true },
    { id: 'practice', label: 'Practice', href: '#practice' },
    { id: 'lexicon', label: 'Lexicon', href: '#lexicon' },
    { id: 'settings', label: 'Settings', href: '#settings' },
  ];
</script>

<nav aria-label="Primary" class="border-t border-violet-100 bg-white/95 px-2 py-2 backdrop-blur dark:border-violet-900/60 dark:bg-slate-950/95">
  <ul class="grid grid-cols-4 gap-2">
    {#each items as item (item.id)}
      <li>
        <a
          href={item.href ?? `#${item.id}`}
          aria-current={item.active ? 'page' : undefined}
          class={`flex min-h-14 items-center justify-center rounded-2xl px-3 py-2 text-center text-sm font-semibold transition ${item.active ? 'bg-violet-600 text-white shadow-sm dark:bg-violet-400 dark:text-slate-950' : 'text-slate-600 hover:bg-violet-50 hover:text-violet-700 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-violet-200'}`}
        >
          {item.label}
        </a>
      </li>
    {/each}
  </ul>
</nav>
