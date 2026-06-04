<script lang="ts">
  export let id = '';
  export let label = '';
  export let value = '';
  export let type: 'text' | 'password' | 'email' | 'search' | 'number' = 'text';
  export let placeholder = '';
  export let disabled = false;
  export let error = '';
  export let autocomplete = 'off';
  export let className = '';

  /** Expose the underlying <input> element so parents can call .focus() etc. */
  let inputElement: HTMLInputElement | undefined;
  export function getInput() { return inputElement; }
</script>

<label class={`flex flex-col gap-2 text-sm font-medium text-slate-700 dark:text-slate-200 ${className}`}>
  {#if label}
    <span>{label}</span>
  {/if}
  <input
    {id}
    {type}
    {placeholder}
    {disabled}
    {autocomplete}
    bind:value
    bind:this={inputElement}
    aria-invalid={error ? 'true' : 'false'}
    class={`w-full rounded-lg border bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus-visible:ring-2 ${error ? 'border-red-400 focus-visible:ring-red-300 dark:border-red-500' : 'border-violet-200 focus-visible:border-violet-400 focus-visible:ring-violet-200 dark:border-violet-800'} dark:bg-slate-950 dark:text-slate-100`}
    on:input
    on:change
    on:blur
    on:focus
  />
  {#if error}
    <span class="text-xs font-medium text-red-600 dark:text-red-400">{error}</span>
  {/if}
</label>