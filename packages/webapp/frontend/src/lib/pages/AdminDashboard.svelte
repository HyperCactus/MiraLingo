<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { deleteAdminUser, getAdminDashboard, type AdminDashboardResponse, type AdminUser } from '../api/admin';
  import AppShell from '../components/layout/AppShell.svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  const dispatch = createEventDispatcher<{
    settings: void;
    logout: void;
  }>();

  export let userName = 'Admin';
  export let navItems = [];

  let state: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let error = '';
  let statusMessage = '';
  let summary: AdminDashboardResponse['summary'] = { total_users: 0, active_7_days: 0, active_30_days: 0 };
  let users: AdminUser[] = [];
  let pendingDeleteId = '';
  let confirmationEmail = '';
  let deleting = false;
  $: selectedUser = users.find((user) => user.id === pendingDeleteId) ?? null;

  const daysCopy = (days: number | null | undefined) => {
    if (days === null || days === undefined) return 'Never active';
    if (days <= 0) return 'Today';
    if (days === 1) return '1 day ago';
    return `${days} days ago`;
  };

  async function loadDashboard() {
    state = users.length ? 'ready' : 'loading';
    error = '';
    try {
      const { response, payload } = await getAdminDashboard();
      if (response.status === 401) {
        dispatch('logout');
        return;
      }
      if (!response.ok || payload.ok === false || !payload.summary || !Array.isArray(payload.users)) {
        state = 'error';
        error = payload.detail ?? 'Could not load admin dashboard.';
        return;
      }
      summary = payload.summary;
      users = payload.users;
      state = 'ready';
    } catch (_error) {
      state = 'error';
      error = 'Could not load admin dashboard.';
    }
  }

  function startDelete(user: AdminUser) {
    pendingDeleteId = user.id;
    confirmationEmail = '';
    error = '';
    statusMessage = '';
  }

  function cancelDelete() {
    pendingDeleteId = '';
    confirmationEmail = '';
  }

  async function confirmDelete() {
    const user = selectedUser;
    if (!user || deleting) return;
    deleting = true;
    error = '';
    statusMessage = '';
    try {
      const { response, payload } = await deleteAdminUser(user.id, confirmationEmail);
      if (!response.ok || payload.ok === false) {
        error = payload.detail ?? 'Could not delete user.';
        return;
      }
      statusMessage = `Deleted ${payload.deleted_email ?? user.email}.`;
      pendingDeleteId = '';
      confirmationEmail = '';
      await loadDashboard();
    } catch (_error) {
      error = 'Could not delete user.';
    } finally {
      deleting = false;
    }
  }

  onMount(() => {
    void loadDashboard();
  });
</script>

<AppShell
  title="Admin"
  subtitle="User activity and account controls"
  userLabel="Admin"
  avatarLabel={userName}
  {navItems}
  showAdmin={true}
  on:admin
  on:settings={() => dispatch('settings')}
  on:logout={() => dispatch('logout')}
>
  <svelte:fragment slot="hero">
    <AppCard className="space-y-4 bg-gradient-to-br from-slate-950 via-violet-950 to-violet-700 text-white shadow-lg">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.28em] text-violet-200">Admin dashboard</p>
        <h1 class="mt-2 text-3xl font-semibold leading-tight sm:text-4xl">User overview</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-violet-100/90 sm:text-base">Only the configured admin account can load these user metrics or delete accounts.</p>
      </div>
      <div class="grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl bg-white/10 p-4 ring-1 ring-white/15">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-100">Total users</p>
          <p class="mt-2 text-3xl font-semibold">{summary?.total_users ?? 0}</p>
        </div>
        <div class="rounded-2xl bg-white/10 p-4 ring-1 ring-white/15">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-100">Active 7 days</p>
          <p class="mt-2 text-3xl font-semibold">{summary?.active_7_days ?? 0}</p>
        </div>
        <div class="rounded-2xl bg-white/10 p-4 ring-1 ring-white/15">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-100">Active 30 days</p>
          <p class="mt-2 text-3xl font-semibold">{summary?.active_30_days ?? 0}</p>
        </div>
      </div>
    </AppCard>
  </svelte:fragment>

  <div class="space-y-4">
    {#if error}
      <AppCard className="border-red-200 bg-red-50 text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"><p role="alert">{error}</p></AppCard>
    {/if}
    {#if statusMessage}
      <AppCard className="border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300"><p>{statusMessage}</p></AppCard>
    {/if}

    <AppCard className="space-y-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">All users</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Last active is based on account updates, practice sessions, shown cards, and answer events.</p>
        </div>
        <AppButton variant="secondary" on:click={() => loadDashboard()} disabled={state === 'loading'}>{state === 'loading' ? 'Refreshing…' : 'Refresh'}</AppButton>
      </div>

      {#if state === 'loading'}
        <p class="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500 dark:bg-slate-900/60 dark:text-slate-400">Loading users…</p>
      {:else if users.length === 0}
        <p class="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500 dark:bg-slate-900/60 dark:text-slate-400">No users found.</p>
      {:else}
        <div class="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800">
          <ul class="divide-y divide-slate-200 dark:divide-slate-800">
            {#each users as user (user.id)}
              <li class="grid gap-3 p-4 sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center">
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">{user.email}</p>
                  <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{daysCopy(user.days_since_last_active)}</p>
                </div>
                <p class="text-sm text-slate-500 dark:text-slate-400 sm:text-right">{user.role ?? 'user'}</p>
                <button
                  type="button"
                  class="inline-flex items-center justify-center gap-2 rounded-lg border border-red-200 bg-transparent px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 dark:border-red-900/60 dark:text-red-300 dark:hover:bg-red-950/30"
                  onclick={() => startDelete(user)}
                >
                  Delete
                </button>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </AppCard>

    {#if selectedUser}
      <AppCard className="space-y-4 border-red-200 bg-red-50/70 dark:border-red-900 dark:bg-red-950/20">
        <div>
          <p class="text-sm font-semibold text-red-800 dark:text-red-200">Confirm account deletion</p>
          <p class="mt-1 text-sm text-red-700 dark:text-red-300">Type <strong>{selectedUser.email}</strong> to delete this account. This revokes sessions and removes owned data through database cascades.</p>
        </div>
        <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
          <span>User email</span>
          <input class="w-full rounded-2xl border border-red-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-200 dark:border-red-900 dark:bg-slate-950 dark:text-slate-50 dark:focus:border-red-500 dark:focus:ring-red-900" bind:value={confirmationEmail} autocomplete="off" />
        </label>
        <div class="flex flex-col gap-3 sm:flex-row">
          <button type="button" class="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-red-300 disabled:opacity-60" disabled={confirmationEmail.trim().toLowerCase() !== selectedUser.email.toLowerCase() || deleting} onclick={() => confirmDelete()}>
            {deleting ? 'Deleting…' : 'Delete account'}
          </button>
          <button type="button" class="inline-flex min-h-12 items-center justify-center gap-2 rounded-lg border border-violet-200 bg-white px-4 py-2 text-sm font-semibold text-violet-700 transition hover:bg-violet-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 dark:border-violet-900 dark:bg-slate-900 dark:text-violet-200 dark:hover:bg-slate-800" onclick={() => cancelDelete()} disabled={deleting}>Cancel</button>
        </div>
      </AppCard>
    {/if}
  </div>

  <svelte:fragment slot="sidebar">
    <AppCard className="space-y-3">
      <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">Security</p>
      <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">Admin metrics and deletes are enforced by server-side session checks against the configured admin email. Hiding the menu is only convenience, not authorization.</p>
    </AppCard>
  </svelte:fragment>
</AppShell>
