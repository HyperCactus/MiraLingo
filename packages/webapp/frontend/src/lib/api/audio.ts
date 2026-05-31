export function getPracticeAudioUrl(cardId: string) {
  return `/practice/audio/${encodeURIComponent(cardId)}`;
}
