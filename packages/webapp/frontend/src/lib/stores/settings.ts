import { writable } from 'svelte/store';

export type AppVoice = {
  id: string;
  label: string;
  provider: string;
  mutable: boolean;
};

export type SoundEffectsMode = 'all' | 'on_answer' | 'ui_only' | 'off';

export type AppSettings = {
  theme: 'light' | 'dark' | 'system';
  ttsSpeed: number;
  ttsAutoplay: boolean;
  soundEffectsEnabled: boolean;
  soundEffectsMode: SoundEffectsMode;
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
  ttsAutoplay: true,
  soundEffectsEnabled: true,
  soundEffectsMode: 'on_answer',
  voice: defaultVoice,
};

export const theme = writable<AppSettings['theme']>(defaultSettings.theme);
export const ttsSpeed = writable(defaultSettings.ttsSpeed);
export const ttsAutoplay = writable(defaultSettings.ttsAutoplay);
export const soundEffectsEnabled = writable(defaultSettings.soundEffectsEnabled);
export const soundEffectsMode = writable<SoundEffectsMode>(defaultSettings.soundEffectsMode);
export const voice = writable<AppVoice>(defaultSettings.voice);
export const settingsLoadedForUser = writable<string | null>(null);

export function applySettingsPayload(payload?: Partial<{ theme: unknown; tts_speed: unknown; tts_autoplay: unknown; sfx_enabled: unknown; voice: Partial<AppVoice> | null; sfx_mode: unknown }>) {
  theme.set(payload?.theme === 'light' || payload?.theme === 'dark' ? payload.theme : 'system');
  const speed = Number(payload?.tts_speed);
  ttsSpeed.set(Number.isFinite(speed) && speed >= 0.5 && speed <= 2 ? speed : defaultSettings.ttsSpeed);
  ttsAutoplay.set(Boolean(payload?.tts_autoplay ?? defaultSettings.ttsAutoplay));

  const modeRaw = payload?.sfx_mode;
  const hasValidMode = modeRaw === 'all' || modeRaw === 'on_answer' || modeRaw === 'ui_only' || modeRaw === 'off';
  const enabledFallback = Boolean(payload?.sfx_enabled ?? defaultSettings.soundEffectsEnabled);
  const mode: SoundEffectsMode = hasValidMode ? (modeRaw as SoundEffectsMode) : (enabledFallback ? 'on_answer' : 'off');

  soundEffectsMode.set(mode);
  soundEffectsEnabled.set(mode === 'all' || mode === 'on_answer');

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
  soundEffectsEnabled.set(defaultSettings.soundEffectsEnabled);
  soundEffectsMode.set(defaultSettings.soundEffectsMode);
  voice.set(defaultVoice);
  settingsLoadedForUser.set(null);
}
