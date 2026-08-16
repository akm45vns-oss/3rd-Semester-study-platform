import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 15000, // 15-second timeout to prevent hanging requests
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT from localStorage on every request
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor with 401 handling, retry for safe GET, and error normalization
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // 1. Handle 401 Unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      sessionStorage.clear();
      if (
        typeof window !== 'undefined' &&
        !['/login', '/register'].includes(window.location.pathname)
      ) {
        window.location.href = '/login?reason=session_expired';
      }
      return Promise.reject(error);
    }

    // 2. Safe GET retry for transient network failure or 503/504
    if (
      config &&
      config.method?.toLowerCase() === 'get' &&
      !config._retry &&
      (!error.response || [502, 503, 504].includes(error.response.status))
    ) {
      config._retry = true;
      try {
        await new Promise((resolve) => setTimeout(resolve, 800));
        return await apiClient(config);
      } catch (retryErr) {
        return Promise.reject(retryErr);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Universal error message extractor that safely handles FastAPI 422 validation arrays,
 * custom error objects, network errors, and raw strings.
 */
export function extractErrorMessage(err: any, fallback: string = 'An error occurred. Please try again.'): string {
  if (!err) return fallback;
  if (typeof err === 'string') return err;

  const detail = err.response?.data?.detail ?? err.response?.data?.message ?? err.message;
  if (!detail) return fallback;
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        if (item && typeof item === 'object') {
          const loc = Array.isArray(item.loc)
            ? item.loc.filter((x: any) => x !== 'body' && x !== 'query').join(' ')
            : '';
          const msg = item.msg || item.message || JSON.stringify(item);
          return loc ? `${loc}: ${msg}` : msg;
        }
        return String(item);
      })
      .join(', ');
  }

  if (typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  return String(detail);
}

export default apiClient;
