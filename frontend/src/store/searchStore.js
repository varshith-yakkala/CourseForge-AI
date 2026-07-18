/**
 * Search state — Zustand. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useSearchStore = create((set) => ({
  query: '',
  results: null,
  isSearching: false,
  setQuery: (query) => set({ query }),
  setResults: (results) => set({ results, isSearching: false }),
  setSearching: (isSearching) => set({ isSearching }),
  clearResults: () => set({ query: '', results: null }),
}))
