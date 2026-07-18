/**
 * Flashcards API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const flashcardsApi = {
  getForCourse: (courseId) => apiClient.get(`/flashcards/course/${courseId}`),
  getDue: (courseId) => apiClient.get(`/flashcards/course/${courseId}/due`),
  recordReview: (flashcardId, rating) => apiClient.post(`/flashcards/${flashcardId}/review`, { rating }),
}
