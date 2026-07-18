/**
 * Auth API module — Phase 2 implementation.
 * POST /auth/register, /auth/login, /auth/refresh, /auth/logout
 * GET  /auth/me, PUT /auth/me
 */
import apiClient from '@/api/client'

export const authApi = {
  /** Register a new user. Phase 2. */
  register: (data) => apiClient.post('/auth/register', data),
  /** Login with email + password. Phase 2. */
  login: (data) => apiClient.post('/auth/login', data),
  /** Get current user profile. Phase 2. */
  me: () => apiClient.get('/auth/me'),
  /** Update user profile. Phase 2. */
  updateMe: (data) => apiClient.put('/auth/me', data),
  /** Logout (invalidate refresh token). Phase 2. */
  logout: () => apiClient.post('/auth/logout'),
}
