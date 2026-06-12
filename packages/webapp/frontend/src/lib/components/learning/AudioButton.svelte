<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import AppButton from '../ui/AppButton.svelte';

  const dispatch = createEventDispatcher<{
    click: MouseEvent;
  }>();

  export let disabled = false;
  export let loading = false;
  export let playing = false;
  export let label = 'Play audio';

  $: buttonLabel = playing ? 'Stop audio' : label;
  $: buttonClass = `audio-button min-h-12 min-w-12 px-3 justify-center rounded-full transition-all ${playing ? 'audio-button-playing' : ''}`;
</script>

<AppButton
  variant="secondary"
  {disabled}
  playClickSound={false}
  className={buttonClass}
  aria-label={buttonLabel}
  aria-pressed={playing}
  on:click={(event) => dispatch('click', event)}
>
  <span aria-hidden="true">{loading ? '…' : playing ? '■' : '🔊'}</span>
</AppButton>

<style>
  :global(.audio-button-playing) {
    background: #7c3aed !important;
    border-color: #8b5cf6 !important;
    color: #ffffff !important;
    box-shadow: 0 12px 24px rgba(124, 58, 237, 0.28) !important;
    outline: 2px solid rgba(196, 181, 253, 0.9);
    outline-offset: 2px;
  }

  :global(.audio-button-playing:hover),
  :global(.audio-button-playing:focus-visible) {
    background: #6d28d9 !important;
    color: #ffffff !important;
  }

  :global(.dark .audio-button-playing) {
    background: #a78bfa !important;
    border-color: #c4b5fd !important;
    color: #0f172a !important;
    box-shadow: 0 12px 24px rgba(167, 139, 250, 0.26) !important;
  }

  :global(.dark .audio-button-playing:hover),
  :global(.dark .audio-button-playing:focus-visible) {
    background: #c4b5fd !important;
    color: #0f172a !important;
  }
</style>
