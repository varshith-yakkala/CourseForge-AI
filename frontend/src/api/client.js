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
    if (token && token !== 'null' && token !== 'undefined') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Response interceptor to handle 401s, automatic refresh, and normalize errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized for token refresh
    if (error.response && error.response.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh' && originalRequest.url !== '/auth/login') {
      const { refreshToken, updateToken, logout } = useAuthStore.getState();
      
      if (!refreshToken) {
        logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
      
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return apiClient(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        const refreshResponse = await axios.post(`${getApiBaseUrl()}/auth/refresh`, {
          refresh_token: refreshToken
        });
        
        const newAccessToken = refreshResponse.data.access_token;
        const newRefreshToken = refreshResponse.data.refresh_token;
        
        updateToken(newAccessToken, newRefreshToken);
        
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
        processQueue(null, newAccessToken);
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
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
