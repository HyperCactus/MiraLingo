export function getPracticeAudioUrl(cardId: string) {
  return `/practice/audio/${encodeURIComponent(cardId)}`;
}

export async function fetchMbrolaTextAudio(text: string) {
  return fetch('/tts/mbrola', {
    method: 'POST',
    headers: { Accept: 'audio/wav,application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
}
