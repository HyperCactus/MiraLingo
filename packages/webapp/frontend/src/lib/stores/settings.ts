import { writable } from 'svelte/store';

export type AppVoice = {
  id: string;
  label: string;
  provider: string;
  mutable: boolean;
};

export type AppSettings = {
  theme: 'light' | 'dark' | 'system';
  ttsSpeed: number;
  ttsAutoplay: boolean;
  voice: AppVoice;
};

const defaultVoice: AppVoice = {
  id: 'de6',
  label: 'Mirad de6',
  provider: 'mbrola',
  mutable: false,
};

const defaultSettings: AppSettings = {
  theme: 'system',
  ttsSpeed: 0.8,
  ttsAutoplay: false,
  voice: defaultVoice,
};

export const theme = writable<AppSettings['theme']>(defaultSettings.theme);
export const ttsSpeed = writable(defaultSettings.ttsSpeed);
export const ttsAutoplay = writable(defaultSettings.ttsAutoplay);
export const voice = writable<AppVoice>(defaultSettings.voice);
export const settingsLoadedForUser = writable<string | null>(null);

export function applySettingsPayload(payload?: Partial<{ theme: unknown; tts_speed: unknown; tts_autoplay: unknown; voice: Partial<AppVoice> | null }>) {
  theme.set(payload?.theme === 'light' || payload?.theme === 'dark' ? payload.theme : 'system');
  const speed = Number(payload?.tts_speed);
  ttsSpeed.set(Number.isFinite(speed) && speed >= 0.5 && speed <= 2 ? speed : defaultSettings.ttsSpeed);
  ttsAutoplay.set(Boolean(payload?.tts_autoplay ?? defaultSettings.ttsAutoplay));
  voice.set({
    id: String(payload?.voice?.id ?? defaultVoice.id),
    label: String(payload?.voice?.label ?? defaultVoice.label),
    provider: String(payload?.voice?.provider ?? defaultVoice.provider),
    mutable: Boolean(payload?.voice?.mutable ?? defaultVoice.mutable),
  });
}

export function resetSettingsStore() {
  theme.set(defaultSettings.theme);
  ttsSpeed.set(defaultSettings.ttsSpeed);
  ttsAutoplay.set(defaultSettings.ttsAutoplay);
  voice.set(defaultVoice);
  settingsLoadedForUser.set(null);
}
