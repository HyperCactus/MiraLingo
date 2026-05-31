export type SessionUser = {
  username: string;
  role?: string;
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
  deleted_username?: string;
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
  });
  const payload = await readJson<CurrentUserResponse>(response);
  return { response, payload };
}

export async function login(username: string, password: string) {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const payload = await readJson<AuthSuccessResponse | AuthFailureResponse>(response);
  return { response, payload };
}

export async function register(username: string, password: string) {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const payload = await readJson<AuthSuccessResponse | AuthFailureResponse>(response);
  return { response, payload };
}

export async function logout() {
  const response = await fetch('/auth/logout', {
    method: 'POST',
    headers: { Accept: 'application/json' },
  });
  const payload = await readJson<{ authenticated?: boolean }>(response);
  return { response, payload };
}

export async function deleteAccount(username: string, confirmation: string) {
  const response = await fetch('/auth/account', {
    method: 'DELETE',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, confirmation }),
  });
  const payload = await readJson<DeleteAccountResponse>(response);
  return { response, payload };
}
