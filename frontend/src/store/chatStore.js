/**
 * Chat global state — Zustand. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useChatStore = create((set) => ({
  sessions: [],
  activeSessionId: null,
  messages: {},
  setActiveSession: (id) => set({ activeSessionId: id }),
  addMessage: (sessionId, message) => set((s) => ({
    messages: { ...s.messages, [sessionId]: [...(s.messages[sessionId] || []), message] },
  })),
}))
