/**
 * Course global state — Zustand store. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useCourseStore = create((set) => ({
  currentCourse: null,
  currentTopic: null,
  setCurrentCourse: (course) => set({ currentCourse: course }),
  setCurrentTopic: (topic) => set({ currentTopic: topic }),
  clearCurrent: () => set({ currentCourse: null, currentTopic: null }),
}))
