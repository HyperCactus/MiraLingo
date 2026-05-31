import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { compile } from 'svelte/compiler';

const files = [
  'src/lib/components/layout/TopBar.svelte',
  'src/lib/components/layout/BottomNav.svelte',
  'src/lib/components/layout/AppShell.svelte',
  'src/lib/components/layout/StudyShell.svelte',
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

test('shell sources encode intended navigation structure', async () => {
  const [appShell, studyShell, bottomNav, topBar] = await Promise.all([
    readFile(new URL('../src/lib/components/layout/AppShell.svelte', import.meta.url), 'utf8'),
    readFile(new URL('../src/lib/components/layout/StudyShell.svelte', import.meta.url), 'utf8'),
    readFile(new URL('../src/lib/components/layout/BottomNav.svelte', import.meta.url), 'utf8'),
    readFile(new URL('../src/lib/components/layout/TopBar.svelte', import.meta.url), 'utf8'),
  ]);

  assert.match(appShell, /BottomNav/);
  assert.match(appShell, /slot name="sidebar"/);
  assert.match(studyShell, /AppCard/);
  assert.doesNotMatch(studyShell, /BottomNav/);
  assert.match(bottomNav, /Dashboard/);
  assert.match(bottomNav, /Practice/);
  assert.match(bottomNav, /Lexicon/);
  assert.match(bottomNav, /Settings/);
  assert.match(topBar, /showBackButton/);
});
