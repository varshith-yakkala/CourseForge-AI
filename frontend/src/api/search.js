/**
 * Search API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const searchApi = {
  search: (query, courseId) => apiClient.get('/search', { params: { q: query, course_id: courseId } }),
}
