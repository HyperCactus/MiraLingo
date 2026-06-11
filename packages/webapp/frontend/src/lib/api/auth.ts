export type SessionUser = {
  id: string;
  email: string;
  name?: string | null;
  role?: 'admin' | 'test_user' | 'user' | string;
  email_verified?: boolean;
};

export type CurrentUserResponse = {
  authenticated: boolean;
  user: SessionUser | null;
  detail?: string;
};

export type AuthSuccessResponse = {
  authenticated: true;
  user: SessionUser;
};

export type AuthFailureResponse = {
  authenticated?: false;
  ok?: false;
  detail?: string;
  error?: string;
  phase?: string;
};

export type DeleteAccountResponse = {
  ok?: boolean;
  phase?: string;
  deleted_email?: string;
  authenticated?: boolean;
  detail?: string;
  error?: string;
};

export async function readJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  try {
    return JSON.parse(text) as T;
  } catch {
    return { error: 'bad json', detail: text } as T;
  }
}

export async function fetchCurrentUser() {
  const response = await fetch('/auth/current-user', {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const payload = await readJson<CurrentUserResponse>(response);
  return { response, payload };
}

export async function login(email: string, password: string) {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });
  const payload = await readJson<AuthSuccessResponse | AuthFailureResponse>(response);
  return { response, payload };
}

export async function register(email: string, password: string, name?: string) {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password, name }),
  });
  const payload = await readJson<AuthSuccessResponse | AuthFailureResponse>(response);
  return { response, payload };
}

export async function requestPasswordReset(email: string) {
  const response = await fetch('/auth/password/forgot', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email }),
  });
  const payload = await readJson<AuthFailureResponse & { ok?: boolean }>(response);
  return { response, payload };
}

export async function resetPassword(token: string, password: string) {
  const response = await fetch('/auth/password/reset', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ token, password }),
  });
  const payload = await readJson<AuthFailureResponse & { ok?: boolean }>(response);
  return { response, payload };
}

export async function logout() {
  const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const payload = await readJson<{ authenticated?: boolean }>(response);
  return { response, payload };
}

export async function deleteAccount(email: string, confirmation: string) {
  const response = await fetch('/auth/account', {
    method: 'DELETE',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, confirmation }),
  });
  const payload = await readJson<DeleteAccountResponse>(response);
  return { response, payload };
}
