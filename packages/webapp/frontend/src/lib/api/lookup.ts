import { readJson } from './auth.ts';

export type LookupDirection = 'en_to_mir' | 'mir_to_en';

export type LookupResult = {
  english: string;
  mirad: string;
  cosine_similarity: number;
  is_exact: boolean;
};

export type LookupErrorCode = 'network_error' | 'http_error' | 'invalid_response';

export class LookupError extends Error {
  code: LookupErrorCode;
  status?: number;
  detail?: string;
  cause?: unknown;

  constructor(message: string, options: { code: LookupErrorCode; status?: number; detail?: string; cause?: unknown }) {
    super(message);
    this.name = 'LookupError';
    this.code = options.code;
    this.status = options.status;
    this.detail = options.detail;
    this.cause = options.cause;
  }
}

type LookupFailureResponse = {
  error?: string;
  detail?: string;
};

function isLookupResultArray(payload: unknown): payload is LookupResult[] {
  return Array.isArray(payload) && payload.every((item) => {
    if (!item || typeof item !== 'object') {
      return false;
    }

    const candidate = item as Record<string, unknown>;
    return (
      typeof candidate.english === 'string' &&
      typeof candidate.mirad === 'string' &&
      typeof candidate.cosine_similarity === 'number' &&
      typeof candidate.is_exact === 'boolean'
    );
  });
}

export async function lookupWord(
  query: string,
  direction: LookupDirection,
  top_k = 3,
): Promise<LookupResult[]> {
  const normalizedQuery = query.trim();
  if (!normalizedQuery) {
    return [];
  }

  const search = new URLSearchParams({
    q: normalizedQuery,
    direction,
    top_k: String(top_k),
  });

  let response: Response;
  try {
    response = await fetch(`/lookup?${search.toString()}`, {
      headers: { Accept: 'application/json' },
    });
  } catch (cause) {
    throw new LookupError('Failed to reach lookup service.', {
      code: 'network_error',
      cause,
    });
  }

  const payload = await readJson<LookupResult[] | LookupFailureResponse>(response);
  if (!response.ok) {
    const failure = payload as LookupFailureResponse;
    throw new LookupError(failure.error || 'Lookup request failed.', {
      code: 'http_error',
      status: response.status,
      detail: failure.detail,
    });
  }

  if (!isLookupResultArray(payload)) {
    throw new LookupError('Lookup service returned an invalid response.', {
      code: 'invalid_response',
      detail: 'Expected an array of lookup results.',
    });
  }

  return payload;
}
