/**
 * UI global state — sidebar, modal, theme. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useUiStore = create((set) => ({
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  activeFocusMode: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  openCommandPalette: () => set({ commandPaletteOpen: true }),
  closeCommandPalette: () => set({ commandPaletteOpen: false }),
  toggleFocusMode: () => set((s) => ({ activeFocusMode: !s.activeFocusMode })),
}))
