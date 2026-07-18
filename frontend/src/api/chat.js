/**
 * Chat API module — Phase 2 implementation.
 */
import apiClient from '@/api/client'

export const chatApi = {
  getSessions: () => apiClient.get('/chat/sessions'),
  createSession: (courseId) => apiClient.post('/chat/sessions', { course_id: courseId }),
  getMessages: (sessionId) => apiClient.get(`/chat/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, message) => apiClient.post('/chat/message', { session_id: sessionId, message }),
}
