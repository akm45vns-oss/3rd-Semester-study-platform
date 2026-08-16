import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../api';
import { extractErrorMessage } from '../api/client';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (data: { username: string; email: string; password: string; full_name?: string }) => Promise<void>;
  logout: (broadcast?: boolean) => void;
  fetchMe: () => Promise<void>;
  clearError: () => void;
}

// Cross-tab broadcast channel
const authChannel = typeof window !== 'undefined' && 'BroadcastChannel' in window
  ? new BroadcastChannel('semester_os_auth_channel')
  : null;

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username, password) => {
        set({ isLoading: true, error: null });
        try {
          const tokenData = await authApi.login(username, password);
          localStorage.setItem('access_token', tokenData.access_token);
          set({ token: tokenData.access_token });
          await get().fetchMe();

          // Broadcast login to other tabs
          authChannel?.postMessage({ type: 'LOGIN', token: tokenData.access_token });
        } catch (err: any) {
          const message = extractErrorMessage(err, 'Login failed. Please check your credentials.');
          set({ error: message, isLoading: false });
          throw err;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await authApi.register(data);
          await get().login(data.username, data.password);
        } catch (err: any) {
          const message = extractErrorMessage(err, 'Registration failed. Please check your inputs.');
          set({ error: message, isLoading: false });
          throw err;
        }
      },

      fetchMe: async () => {
        set({ isLoading: true });
        try {
          const user = await authApi.me();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          localStorage.removeItem('access_token');
          set({ user: null, token: null, isAuthenticated: false, isLoading: false });
        }
      },

      logout: (broadcast = true) => {
        localStorage.removeItem('access_token');
        sessionStorage.clear();
        set({ user: null, token: null, isAuthenticated: false });

        if (broadcast) {
          authChannel?.postMessage({ type: 'LOGOUT' });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({ token: state.token }),
    }
  )
);

// Cross-tab synchronization listeners
if (typeof window !== 'undefined') {
  // BroadcastChannel listener
  authChannel?.addEventListener('message', (event) => {
    if (event.data?.type === 'LOGOUT') {
      useAuthStore.getState().logout(false);
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
  });

  // Storage listener fallback
  window.addEventListener('storage', (e) => {
    if (e.key === 'access_token' && !e.newValue) {
      useAuthStore.getState().logout(false);
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
  });
}
