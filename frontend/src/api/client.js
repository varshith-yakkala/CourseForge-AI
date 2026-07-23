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
  timeout: 15000,
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

// Response interceptor to handle 401s (logout) safely and normalize errors
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
    
    // Normalize errors
    let errorMessage = 'An unexpected error occurred. Please try again.';
    
    if (error.response) {
      // Server responded with an error
      if (error.response.data && error.response.data.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail;
        }
      } else if (error.response.data && error.response.data.errors && error.response.data.errors.length > 0) {
        errorMessage = error.response.data.errors[0].msg || 'Validation error';
      }
    } else if (error.request) {
      // Network error or timeout
      errorMessage = 'Unable to reach the server. Please check your connection or try again later.';
    } else {
      errorMessage = error.message;
    }
    
    error.normalizedMessage = errorMessage;
    
    return Promise.reject(error);
  }
);
