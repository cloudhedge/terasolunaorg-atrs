/**
 * Auth API hooks with TanStack Query
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../stores/authStore';
import type { LoginResponse, User } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '';

export function useLogin() {
  const login = useAuthStore((state) => state.login);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (credentials: { username: string; password: string }) => {
      // OAuth2 password flow requires form-urlencoded
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Login failed');
      }

      return response.json() as Promise<LoginResponse>;
    },
    onSuccess: (data) => {
      login(data.access_token, {
        membershipNumber: data.membership_number,
        name: data.membership_number, // Will be updated by /me
      });
      queryClient.invalidateQueries({ queryKey: ['me'] });
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((state) => state.logout);
  const queryClient = useQueryClient();
  const token = useAuthStore((state) => state.token);

  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_BASE}/api/v1/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });
      
      if (!response.ok) {
        throw new Error('Logout failed');
      }
      
      return response.json();
    },
    onSuccess: () => {
      logout();
      queryClient.clear();
    },
    onError: () => {
      // Logout locally even if API fails
      logout();
      queryClient.clear();
    },
  });
}

export function useMe() {
  const { isAuthenticated, token, updateUser } = useAuthStore();

  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch user');
      }
      
      const data = await response.json() as User;
      updateUser(data);
      return data;
    },
    enabled: isAuthenticated && !!token,
    retry: false,
  });
}
