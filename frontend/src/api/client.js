import axios from 'axios';
import { useAuthStore } from '../store/useAuthStore';

/**
 * Safely normalizes the API base URL.
 * Accepts:
 *  - https://courseforge-backend-iqi6.onrender.com
 *  - https://courseforge-backend-iqi6.onrender.com/api/v1
 *  - http://localhost:8001
 * Outputs:
 *  - https://courseforge-backend-iqi6.onrender.com/api/v1
 */
const getApiBaseUrl = () => {
  const rawUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  const cleanUrl = rawUrl.trim().replace(/\/+$/, '');
  if (cleanUrl.endsWith('/api/v1')) {
    return cleanUrl;
  }
  return `${cleanUrl}/api/v1`;
};

// Base API configuration
export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401s (logout) safely
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const { logout } = useAuthStore.getState();
      logout();
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
