import { writable } from 'svelte/store';
import type { SessionUser } from '../api/auth';

export type AuthState = 'checking' | 'anonymous' | 'authenticated' | 'login-failed' | 'registration-failed';

export const currentUser = writable<SessionUser | null>(null);
export const authState = writable<AuthState>('checking');
export const authError = writable('');
export const authMessage = writable('');

export function clearAuthFeedback() {
  authError.set('');
  authMessage.set('');
}

export function setAuthenticated(user: SessionUser) {
  currentUser.set(user);
  authState.set('authenticated');
  clearAuthFeedback();
}

export function setAnonymous(message = '') {
  currentUser.set(null);
  authState.set('anonymous');
  authError.set('');
  authMessage.set(message);
}

export function setAuthFailure(state: Extract<AuthState, 'login-failed' | 'registration-failed'>, message: string) {
  currentUser.set(null);
  authState.set(state);
  authError.set(message);
  authMessage.set('');
}

export function resetAuthStore(message = '') {
  currentUser.set(null);
  authState.set('anonymous');
  authError.set('');
  authMessage.set(message);
}
