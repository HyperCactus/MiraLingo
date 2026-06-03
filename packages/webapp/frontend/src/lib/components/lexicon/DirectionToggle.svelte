<script lang="ts">
  import type { LookupDirection } from '../../api/lookup.ts';

  export let value: LookupDirection = 'en_to_mir';
  export let disabled = false;

  const options: Array<{ value: LookupDirection; label: string; description: string }> = [
    { value: 'en_to_mir', label: 'En to Mir', description: 'Search with an English source word.' },
    { value: 'mir_to_en', label: 'Mir to En', description: 'Search with a Mirad source word.' },
  ];
</script>

<fieldset class="space-y-2" aria-label="Search direction">
  <legend class="text-sm font-semibold text-slate-900 dark:text-slate-100">Direction</legend>
  <div class="inline-flex rounded-2xl border border-violet-100 bg-slate-50 p-1 dark:border-violet-900/60 dark:bg-slate-900/70">
    {#each options as option}
      <label class="min-w-[8.5rem] cursor-pointer">
        <input class="sr-only" type="radio" name="lookup-direction" bind:group={value} value={option.value} {disabled} />
        <span
          class={`pointer-events-none flex flex-col rounded-xl px-4 py-3 text-left text-sm transition ${value === option.value ? 'bg-violet-600 text-white shadow-sm dark:bg-violet-400 dark:text-slate-950' : 'text-slate-600 hover:bg-violet-50 hover:text-violet-700 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-violet-200'} ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
        >
          <span class="font-semibold">{option.label}</span>
          <span class={`text-xs ${value === option.value ? 'text-violet-100 dark:text-slate-700' : 'text-slate-400 dark:text-slate-500'}`}>
            {option.description}
          </span>
        </span>
      </label>
    {/each}
  </div>
</fieldset>
