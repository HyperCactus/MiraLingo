import { readJson } from './auth';

export type PracticeMode = 'mixed' | 'revision' | 'build_vocabulary';

export type PracticeCard = {
  id: string;
  base_card_id?: string;
  audio_card_id?: string;
  prompt?: string;
  answer?: string;
  prompt_language?: string;
  answer_language?: string;
  type?: string;
  intro_mode?: boolean;
};

export type PracticeQueueResponse = {
  ok?: boolean;
  detail?: string;
  error?: string;
  phase?: string;
  practice_phase?: string;
  cards?: PracticeCard[];
  [key: string]: unknown;
};

export type PracticeAnswerRequest = {
  card_id: string;
  answer?: string;
  correct?: boolean;
};

export type PracticeAchievement = {
  id: string;
  kind?: string;
  threshold?: number;
  title?: string;
  message?: string;
  highlighted_base_card_id?: string;
  highlighted_pair?: { english?: string; mirad?: string };
  sound?: string;
};

export type PracticeAnswerResponse = {
  ok?: boolean;
  detail?: string;
  error?: string;
  expected_answer?: string;
  submitted_answer?: string;
  correct?: boolean;
  achievements?: PracticeAchievement[];
  [key: string]: unknown;
};

export type PracticeProgressResponse = {
  ok?: boolean;
  detail?: string;
  error?: string;
  accuracy?: number;
  event_count?: number;
  weak_count?: number;
  mastered_count?: number;
  stale_count?: number;
  new_count?: number;
  [key: string]: unknown;
};

export type PracticeAnalyticsResponse = {
  ok?: boolean;
  detail?: string;
  error?: string;
  phase?: string;
  event_count?: number;
  accuracy?: number;
  session_count?: number;
  lifecycle_count?: number;
  sparse_history?: boolean;
  timing?: Record<string, unknown>;
  streak?: Record<string, unknown>;
  lifecycle?: Record<string, unknown>;
  direction_breakdown?: Record<string, unknown>;
  card_type_breakdown?: Record<string, unknown>;
  per_card?: unknown[];
  [key: string]: unknown;
};

export async function getPracticeQueue(mode: PracticeMode, limit = 8) {
  const query = new URLSearchParams({ mode, limit: String(limit) });
  const response = await fetch(`/practice/queue?${query.toString()}`, {
    headers: { Accept: 'application/json' },
  });
  const payload = await readJson<PracticeQueueResponse>(response);
  return { response, payload };
}

export async function submitPracticeAnswer(body: PracticeAnswerRequest) {
  const response = await fetch('/practice/answers', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const payload = await readJson<PracticeAnswerResponse>(response);
  return { response, payload };
}

export async function getPracticeProgress() {
  const response = await fetch('/practice/progress', {
    headers: { Accept: 'application/json' },
  });
  const payload = await readJson<PracticeProgressResponse>(response);
  return { response, payload };
}

export async function getPracticeAnalytics() {
  const response = await fetch('/practice/analytics', {
    headers: { Accept: 'application/json' },
  });
  const payload = await readJson<PracticeAnalyticsResponse>(response);
  return { response, payload };
}
