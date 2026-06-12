<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppButton from '../components/ui/AppButton.svelte';
  import AppCard from '../components/ui/AppCard.svelte';

  const dispatch = createEventDispatcher<{
    submit: void;
    cancel: void;
  }>();

  let {
    newPassword = $bindable(''),
    confirmPassword = $bindable(''),
    submitting = false,
    error = '',
    message = '',
  } = $props();
</script>

<div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-50">
  <main class="mx-auto flex min-h-screen max-w-xl flex-col justify-center px-4 py-8 sm:px-6">
    <AppCard className="space-y-5">
      <div class="space-y-2">
        <p class="text-sm font-semibold uppercase tracking-[0.22em] text-violet-600 dark:text-violet-300">Reset password</p>
        <h1 class="text-3xl font-semibold text-slate-900 dark:text-slate-50">Choose a new password</h1>
        <p class="text-sm leading-6 text-slate-500 dark:text-slate-400">
          Enter and confirm your new MiraLingo password. Passwords must be 8 to 128 characters.
        </p>
      </div>

      {#if error}
        <div class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300" role="alert">{error}</div>
      {/if}
      {#if message}
        <div class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200" role="status">{message}</div>
      {/if}

      <form class="space-y-4" onsubmit={(event) => { event.preventDefault(); dispatch('submit'); }}>
        <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
          <span>New password</span>
          <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="new-password" bind:value={newPassword} minlength="8" maxlength="128" required type="password" />
        </label>
        <label class="block space-y-2 text-sm font-medium text-slate-700 dark:text-slate-200">
          <span>Confirm new password</span>
          <input class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-base text-slate-900 shadow-sm outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-200 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-50 dark:focus:border-violet-500 dark:focus:ring-violet-900" autocomplete="new-password" bind:value={confirmPassword} minlength="8" maxlength="128" required type="password" />
        </label>
        <AppButton type="submit" className="min-h-12 w-full justify-center">{submitting ? 'Resetting…' : 'Reset Password'}</AppButton>
        <AppButton type="button" variant="secondary" className="min-h-12 w-full justify-center" on:click={() => dispatch('cancel')}>Back to Log In</AppButton>
      </form>
    </AppCard>
  </main>
</div>
