<script lang="ts">
  import AppInput from '../ui/AppInput.svelte';

  export let label = 'Your answer';
  export let placeholder = 'Type your answer';
  export let value = '';
  export let disabled = false;
  export let error = '';

  /** Expose the underlying <input> element so parents can call .focus() etc. */
  export function getInput() { return appInputRef?.getInput(); }

  let appInputRef: AppInput;
</script>

<AppInput
  id="exercise-answer"
  autocomplete="off"
  bind:value
  {disabled}
  {error}
  {label}
  {placeholder}
  className="w-full"
  bind:this={appInputRef}
/>