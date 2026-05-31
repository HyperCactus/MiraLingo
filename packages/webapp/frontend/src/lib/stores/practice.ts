import { writable } from 'svelte/store';
import type { PracticeMode } from '../api/practice';

export type AppSection = 'welcome' | 'dashboard' | 'practice' | 'analytics' | 'settings' | 'lexicon' | 'revision' | 'build_vocabulary';

export const currentMode = writable<PracticeMode>('mixed');
export const currentSection = writable<AppSection>('welcome');

export function setCurrentSection(section: AppSection) {
  currentSection.set(section);
}

export function goToDashboard() {
  currentSection.set('dashboard');
}

export function setPracticeMode(mode: PracticeMode) {
  currentMode.set(mode);
  currentSection.set(
    mode === 'revision' ? 'revision' : mode === 'build_vocabulary' ? 'build_vocabulary' : 'practice'
  );
}

export function resetPracticeNavigation() {
  currentMode.set('mixed');
  currentSection.set('welcome');
}
