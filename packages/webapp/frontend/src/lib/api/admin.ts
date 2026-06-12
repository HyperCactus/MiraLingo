import { readJson } from './auth';

export type AdminUser = {
  id: string;
  email: string;
  name?: string | null;
  role?: string;
  last_active_at?: string | null;
  days_since_last_active?: number | null;
};

export type AdminDashboardResponse = {
  ok?: boolean;
  phase?: string;
  summary?: {
    total_users: number;
    active_7_days: number;
    active_30_days: number;
  };
  users?: AdminUser[];
  detail?: string;
  error?: string;
};

export type AdminDeleteUserResponse = {
  ok?: boolean;
  phase?: string;
  deleted_user_id?: string;
  deleted_email?: string;
  detail?: string;
  error?: string;
};

export async function getAdminDashboard() {
  const response = await fetch('/admin/dashboard', {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  const payload = await readJson<AdminDashboardResponse>(response);
  return { response, payload };
}

export async function deleteAdminUser(userId: string, confirmationEmail: string) {
  const response = await fetch(`/admin/users/${encodeURIComponent(userId)}`, {
    method: 'DELETE',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ confirmation_email: confirmationEmail }),
  });
  const payload = await readJson<AdminDeleteUserResponse>(response);
  return { response, payload };
}
