<script lang="ts">
  import AppButton from '../ui/AppButton.svelte';

  export let disabled = false;
  export let loading = false;
  export let label = 'Play audio';
</script>

<AppButton variant="secondary" {disabled} className="w-full justify-center sm:w-auto" aria-label={label}>
  <span aria-hidden="true">🔊</span>
  <span>{loading ? 'Preparing…' : label}</span>
</AppButton>
