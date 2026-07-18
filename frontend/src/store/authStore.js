/**
 * Auth global state — Zustand store. Phase 2 implementation.
 * Stores: user, accessToken, isAuthenticated
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setAccessToken: (token) => set({ accessToken: token }),
      logout: () => set({ user: null, accessToken: null, isAuthenticated: false }),
    }),
    { name: 'courseforge-auth', partialize: (s) => ({ accessToken: s.accessToken }) }
  )
)
