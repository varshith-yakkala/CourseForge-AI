/**
 * Quiz session state — Zustand. Phase 2 implementation.
 */
import { create } from 'zustand'

export const useQuizStore = create((set) => ({
  activeAttemptId: null,
  questions: [],
  answers: {},
  currentIndex: 0,
  setAttempt: (attemptId, questions) => set({ activeAttemptId: attemptId, questions, answers: {}, currentIndex: 0 }),
  setAnswer: (questionId, answer) => set((s) => ({ answers: { ...s.answers, [questionId]: answer } })),
  nextQuestion: () => set((s) => ({ currentIndex: Math.min(s.currentIndex + 1, s.questions.length - 1) })),
  prevQuestion: () => set((s) => ({ currentIndex: Math.max(s.currentIndex - 1, 0) })),
  resetQuiz: () => set({ activeAttemptId: null, questions: [], answers: {}, currentIndex: 0 }),
}))
