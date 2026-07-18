/**
 * Quiz API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const quizApi = {
  getForLesson: (lessonId) => apiClient.get(`/quiz/lesson/${lessonId}`),
  startAttempt: (quizId) => apiClient.post(`/quiz/${quizId}/attempt`),
  submit: (attemptId, answers) => apiClient.post(`/quiz/attempts/${attemptId}/submit`, { answers }),
  getResult: (attemptId) => apiClient.get(`/quiz/attempts/${attemptId}`),
}
