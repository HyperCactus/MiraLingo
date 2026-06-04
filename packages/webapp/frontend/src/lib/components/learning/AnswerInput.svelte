<script lang="ts">
  import AppInput from '../ui/AppInput.svelte';

  export let label = 'Your answer';
  export let placeholder = 'Type your answer';
  export let value = '';
  export let disabled = false;
  export let error = '';
  export let inputEl: HTMLInputElement | undefined = $bindable();
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
  bind:inputEl
/>
