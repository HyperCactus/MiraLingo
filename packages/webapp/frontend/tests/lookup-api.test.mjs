import test from 'node:test';
import assert from 'node:assert/strict';

import { LookupError, lookupWord } from '../src/lib/api/lookup.ts';

const originalFetch = globalThis.fetch;

test.after(() => {
  globalThis.fetch = originalFetch;
});

test('lookupWord returns parsed lookup results for a successful response', async () => {
  let requestedUrl = '';
  globalThis.fetch = async (url, options) => {
    requestedUrl = String(url);
    assert.deepEqual(options?.headers, { Accept: 'application/json' });

    return new Response(
      JSON.stringify([
        {
          english: 'run',
          mirad: 'xebwa',
          cosine_similarity: 0.91,
          is_exact: false,
        },
      ]),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      },
    );
  };

  const results = await lookupWord(' run ', 'en_to_mir');

  assert.equal(requestedUrl, '/lookup?q=run&direction=en_to_mir&top_k=3');
  assert.deepEqual(results, [
    {
      english: 'run',
      mirad: 'xebwa',
      cosine_similarity: 0.91,
      is_exact: false,
    },
  ]);
});

test('lookupWord returns an empty array for blank queries without calling fetch', async () => {
  let called = false;
  globalThis.fetch = async () => {
    called = true;
    throw new Error('fetch should not be called');
  };

  const results = await lookupWord('   ', 'mir_to_en');

  assert.deepEqual(results, []);
  assert.equal(called, false);
});

test('lookupWord throws a typed LookupError on HTTP failures', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ error: 'semantic search unavailable' }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' },
  });

  await assert.rejects(
    () => lookupWord('run', 'en_to_mir'),
    (error) => {
      assert.ok(error instanceof LookupError);
      assert.equal(error.code, 'http_error');
      assert.equal(error.status, 503);
      assert.equal(error.message, 'semantic search unavailable');
      return true;
    },
  );
});

test('lookupWord throws a typed LookupError on network failures', async () => {
  globalThis.fetch = async () => {
    throw new TypeError('network down');
  };

  await assert.rejects(
    () => lookupWord('run', 'en_to_mir'),
    (error) => {
      assert.ok(error instanceof LookupError);
      assert.equal(error.code, 'network_error');
      assert.equal(error.message, 'Failed to reach lookup service.');
      return true;
    },
  );
});
