<script lang="ts">
  import { createEventDispatcher, tick } from 'svelte';
  import AppButton from '../ui/AppButton.svelte';
  import AppCard from '../ui/AppCard.svelte';
  import type { PracticeCard, PracticeAnswerResponse } from '../../api/practice';
  import AnswerInput from './AnswerInput.svelte';
  import ExercisePrompt from './ExercisePrompt.svelte';
  import FeedbackPanel from './FeedbackPanel.svelte';

  const dispatch = createEventDispatcher<{
    submit: { answer: string };
    reveal: void;
    continue: void;
    audio: void;
    lookup: { word: string; language: 'english' | 'mirad'; anchorRect: DOMRect };
  }>();

  export let card: PracticeCard | null = null;
  export let answer = '';
  export let answerError = '';
  export let practiceError = '';
  export let submitting = false;
  export let answerResult: PracticeAnswerResponse | null = null;
  export let audioLoading = false;
  export let audioMessage = '';
  export let audioEnabled = false;

  let inputEl: HTMLInputElement | undefined = $state();

  $effect(() => {
    // Re-focus the answer input whenever a new card arrives
    if (card?.id && !answerResult) {
      tick().then(() => inputEl?.focus());
    }
  });

  const showPromptAudio = (currentCard: PracticeCard | null, enabled: boolean) => Boolean(
    currentCard && currentCard.prompt_language === 'mirad' && !answerResult && enabled
  );

  const languageLabel = (value?: string) => {
    const normalized = String(value ?? '').trim().toLowerCase();
    return normalized === 'mirad' ? 'Mirad' : normalized === 'english' ? 'English' : 'Practice';
  };

  const inputLabel = (currentCard: PracticeCard | null) => `Your ${languageLabel(currentCard?.answer_language)} answer`;
  const inputPlaceholder = (currentCard: PracticeCard | null) => `Type the ${languageLabel(currentCard?.answer_language).toLowerCase()} answer`;
  const promptEyebrow = (currentCard: PracticeCard | null) => `${languageLabel(currentCard?.prompt_language)} prompt`;

  function submit() {
    dispatch('submit', { answer: answer.trim() });
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && answerResult) {
      event.preventDefault();
      dispatch('continue');
    }
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<AppCard className="mx-auto w-full max-w-sm space-y-5 rounded-[2rem] p-5 shadow-lg sm:max-w-md sm:p-6">
  {#if card}
    <ExercisePrompt
      eyebrow={promptEyebrow(card)}
      text={card.prompt ?? 'Prompt unavailable'}
      language={(card.prompt_language === 'mirad' ? 'mirad' : 'english')}
      supportingText=""
      canPlayAudio={showPromptAudio(card, audioEnabled)}
      {audioLoading}
      on:audio={() => dispatch('audio')}
      on:lookup={(event) => dispatch('lookup', event.detail)}
    />

    {#if !answerResult}
      <form class="space-y-4" on:submit|preventDefault={submit}>
        <AnswerInput
          bind:value={answer}
          bind:inputEl
          disabled={submitting}
          error={answerError || practiceError}
          label={inputLabel(card)}
          placeholder={inputPlaceholder(card)}
        />

        <div class="grid gap-3">
          <AppButton type="submit" disabled={submitting || !answer.trim()} className="min-h-12 w-full justify-center">
            {submitting ? 'Checking…' : 'Submit answer'}
          </AppButton>
          <AppButton
            variant="secondary"
            disabled={submitting}
            className="min-h-12 w-full justify-center"
            playClickSound={false}
            on:click={() => dispatch('reveal')}
          >
            Show answer
          </AppButton>
        </div>

        {#if audioMessage}
          <p class="text-sm text-slate-500 dark:text-slate-400">{audioMessage}</p>
        {/if}
      </form>
    {:else}
      <FeedbackPanel
        audioLoading={audioLoading}
        audioLabel={'Play Mirad audio'}
        audioMessage={audioMessage}
        canPlayAudio={audioEnabled}
        correct={Boolean(answerResult.correct)}
        revealedAnswer={answerResult.expected_answer ?? card.answer ?? ''}
        submittedAnswer={answerResult.submitted_answer ?? answer.trim()}
        answerLanguage={(card.answer_language === 'mirad' ? 'mirad' : 'english')}
        on:audio={() => dispatch('audio')}
        on:lookup={(event) => dispatch('lookup', event.detail)}
      />

      <AppButton className="min-h-12 w-full justify-center" on:click={() => dispatch('continue')}>
        Continue
      </AppButton>
    {/if}
  {:else}
    <div class="space-y-2 py-8 text-center text-sm text-slate-500 dark:text-slate-400">
      <p class="font-semibold text-slate-700 dark:text-slate-200">Practice card unavailable</p>
      <p>Load a study item to continue the exercise flow.</p>
    </div>
  {/if}
</AppCard>
