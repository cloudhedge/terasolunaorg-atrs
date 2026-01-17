/**
 * API client with auth token injection
 */
import { useAuthStore } from '../stores/authStore';

const API_BASE = import.meta.env.VITE_API_URL || '';

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(status: number, code?: string, message?: string) {
    super(message || `HTTP ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = useAuthStore.getState().token;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}/api/v1${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 - auto logout
  if (response.status === 401) {
    useAuthStore.getState().logout();
    throw new ApiError(401, 'UNAUTHORIZED', 'Session expired');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      error.code,
      error.message || error.detail
    );
  }

  // Handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : (null as unknown as T);
}

// Convenience methods
export const api = {
  get: <T>(endpoint: string) => apiClient<T>(endpoint),

  post: <T>(endpoint: string, data?: unknown) =>
    apiClient<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data: unknown) =>
    apiClient<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: <T>(endpoint: string) =>
    apiClient<T>(endpoint, { method: 'DELETE' }),
};
