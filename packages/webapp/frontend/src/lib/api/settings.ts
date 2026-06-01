import { readJson } from './auth';

export type UserSettings = {
  theme: 'light' | 'dark' | 'system';
  tts_speed: number;
  tts_autoplay: boolean;
  sfx_enabled: boolean;
  voice?: {
    id: string;
    label: string;
    provider: string;
    mutable: boolean;
  };
};

export type SettingsResponse = {
  ok?: boolean;
  phase?: string;
  detail?: string;
  error?: string;
  settings?: UserSettings;
};

export async function getSettings() {
  const response = await fetch('/settings', {
    headers: { Accept: 'application/json' },
  });
  const payload = await readJson<SettingsResponse>(response);
  return { response, payload };
}

export async function updateSettings(settings: Pick<UserSettings, 'theme' | 'tts_speed' | 'tts_autoplay' | 'sfx_enabled'>) {
  const response = await fetch('/settings', {
    method: 'PUT',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  const payload = await readJson<SettingsResponse>(response);
  return { response, payload };
}
