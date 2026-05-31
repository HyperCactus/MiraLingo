export function getPracticeAudioUrl(cardId: string) {
  return `/practice/audio/${encodeURIComponent(cardId)}`;
}

export function buildLexiconPracticeAudioCardId(miradWord: string) {
  const normalized = miradWord.trim().toLowerCase();
  return normalized ? `word:${normalized}` : '';
}
