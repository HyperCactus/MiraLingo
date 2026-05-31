import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { compile } from 'svelte/compiler';

const files = [
  'src/lib/components/lexicon/DirectionToggle.svelte',
  'src/lib/components/lexicon/LexiconResultRow.svelte',
  'src/lib/pages/Lexicon.svelte',
];

for (const file of files) {
  test(`${file} compiles`, async () => {
    const source = await readFile(new URL(`../${file}`, import.meta.url), 'utf8');
    const result = compile(source, {
      filename: file,
      generate: 'dom',
      modernAst: true,
    });

    assert.ok(result.js.code.includes('create_fragment') || result.js.code.length > 0);
  });
}

test('lexicon page source encodes debounce, empty, no-results, error, and audio fallback states', async () => {
  const source = await readFile(new URL('../src/lib/pages/Lexicon.svelte', import.meta.url), 'utf8');

  assert.match(source, /const debounceMs = 300/);
  assert.match(source, /lookupWord\(expectedQuery, expectedDirection\)/);
  assert.match(source, /Type a word to find similar Mirad translations/);
  assert.match(source, /Type a word to find similar English translations/);
  assert.match(source, /Search unavailable right now — try again later/);
  assert.match(source, /No similar words found for '\$\{normalizedQuery\}'\./);
  assert.match(source, /buildLexiconPracticeAudioCardId/);
  assert.match(source, /getPracticeAudioUrl\(cardId\)/);
  assert.match(source, /Audio preview tries <code>\/practice\/audio\/word:&lt;mirad&gt;<\/code>/);
  assert.match(source, /speechSynthesis/);
});

test('app route source imports and renders the Lexicon page', async () => {
  const source = await readFile(new URL('../src/App.svelte', import.meta.url), 'utf8');

  assert.match(source, /import Lexicon from "\.\/lib\/pages\/Lexicon\.svelte";/);
  assert.match(source, /\$currentSection === "lexicon"/);
  assert.match(source, /<Lexicon/);
  assert.match(source, /on:back=\{goToMenu\}/);
  assert.match(source, /label: "Lexicon"/);
});
