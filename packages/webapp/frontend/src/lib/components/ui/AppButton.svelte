<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { get } from 'svelte/store';
  import { soundEffectsEnabled, soundEffectsMode } from '../../stores/settings';

  export let variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  export let type: 'button' | 'submit' | 'reset' = 'button';
  export let disabled = false;
  export let className = '';
  export let soundEffectSrc = '/assets/sound_effects/ui_button.wav';
  export let playClickSound = true;
  export let soundEffectVolume = 0.18;

  const dispatch = createEventDispatcher<{ click: MouseEvent }>();

  const variantClasses = {
    primary: 'bg-violet-600 text-white hover:bg-violet-700 focus-visible:ring-violet-500 disabled:bg-violet-300 dark:bg-violet-400 dark:text-slate-950 dark:hover:bg-violet-300',
    secondary: 'border border-violet-200 bg-white text-violet-700 hover:bg-violet-50 focus-visible:ring-violet-400 dark:border-violet-900 dark:bg-slate-900 dark:text-violet-200 dark:hover:bg-slate-800',
    ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 focus-visible:ring-slate-400 dark:text-slate-200 dark:hover:bg-slate-800',
  };

  async function handleClick(event: MouseEvent) {
    dispatch('click', event);
    if (!playClickSound || disabled || !get(soundEffectsEnabled) || get(soundEffectsMode) !== 'all' || !soundEffectSrc) return;
    try {
      const audio = new Audio(soundEffectSrc);
      audio.volume = Math.max(0, Math.min(1, Number(soundEffectVolume) || 0));
      await audio.play();
    } catch (_) {
      // Non-blocking UX hint only.
    }
  }
</script>

<button
  {type}
  {disabled}
  class={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 ${variantClasses[variant]} ${className}`}
  on:click={handleClick}
>
  <slot />
</button>
