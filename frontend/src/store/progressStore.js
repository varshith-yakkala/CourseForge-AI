/**
 * Progress state — Zustand. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useProgressStore = create((set) => ({
  courseProgress: {},
  setCourseProgress: (courseId, progress) => set((s) => ({
    courseProgress: { ...s.courseProgress, [courseId]: progress },
  })),
}))
