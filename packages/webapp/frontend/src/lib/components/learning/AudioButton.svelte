<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppButton from '../ui/AppButton.svelte';

  const dispatch = createEventDispatcher<{
    click: MouseEvent;
  }>();

  export let disabled = false;
  export let loading = false;
  export let label = 'Play audio';
</script>

<AppButton
  variant="secondary"
  {disabled}
  playClickSound={false}
  className="min-h-12 min-w-12 px-3 justify-center rounded-full"
  aria-label={label}
  on:click={(event) => dispatch('click', event)}
>
  <span aria-hidden="true">{loading ? '…' : '🔊'}</span>
</AppButton>
