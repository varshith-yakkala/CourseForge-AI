import { apiClient } from './client';

export const authApi = {
  login: async (credentials) => {
    const { data } = await apiClient.post('/auth/login', credentials);
    return data;
  },
  register: async (userData) => {
    const { data } = await apiClient.post('/auth/register', userData);
    return data;
  },
  getMe: async () => {
    const { data } = await apiClient.get('/auth/me');
    return data;
  },
};

export const coursesApi = {
  getAll: async () => {
    const { data } = await apiClient.get('/courses');
    return data;
  },
  getById: async (id) => {
    const { data } = await apiClient.get(`/courses/${id}`);
    return data;
  },
  create: async (courseData) => {
    const { data } = await apiClient.post('/courses', courseData);
    return data;
  },
  update: async (id, courseData) => {
    const { data } = await apiClient.put(`/courses/${id}`, courseData);
    return data;
  },
  delete: async (id) => {
    await apiClient.delete(`/courses/${id}`);
    return id;
  },
  generate: async (id) => {
    const { data } = await apiClient.post(`/courses/${id}/generate`);
    return data;
  },
  getStructure: async (id) => {
    const { data } = await apiClient.get(`/courses/${id}/structure`);
    return data;
  }
};

export const documentsApi = {
  upload: async (courseId, file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('course_id', courseId);
    formData.append('file', file);
    
    const { data } = await apiClient.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return data;
  },
  getById: async (id) => {
    const { data } = await apiClient.get(`/documents/${id}`);
    return data;
  },
  getByCourseId: async (courseId) => {
    const { data } = await apiClient.get(`/documents/course/${courseId}`);
    return data;
  },
  retry: async (id) => {
    const { data } = await apiClient.post(`/documents/${id}/retry`);
    return data;
  },
};

export const searchApi = {
  search: async (query, courseId = null) => {
    const { data } = await apiClient.post('/search', { query, course_id: courseId });
    return data;
  },
};

export const lessonsApi = {
  getLesson: async (courseId, lessonId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/lessons/${lessonId}`);
    return data;
  },
  generate: async (courseId, lessonId) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/generate`);
    return data;
  },
  regenerate: async (courseId, lessonId) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/regenerate`);
    return data;
  },
  updateProgress: async (courseId, lessonId, progressData) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/progress`, progressData);
    return data;
  },
  getCourseProgress: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/progress`);
    return data;
  },
  askTutor: async (courseId, lessonId, question) => {
    const { data } = await apiClient.post(`/courses/${courseId}/lessons/${lessonId}/ask`, { question });
    return data;
  },
};

export const quizzesApi = {
  getQuiz: async (courseId, lessonId, difficulty = 'Intermediate', numQuestions = 10) => {
    const { data } = await apiClient.get(`/courses/${courseId}/lessons/${lessonId}/quiz`, {
      params: { difficulty, num_questions: numQuestions },
    });
    return data;
  },
  submitAttempt: async (quizId, attemptData) => {
    const { data } = await apiClient.post(`/quizzes/${quizId}/submit`, attemptData);
    return data;
  },
};

export const flashcardsApi = {
  getDeck: async (courseId, lessonId = null, mode = 'all') => {
    const { data } = await apiClient.get(`/courses/${courseId}/flashcards`, {
      params: { lesson_id: lessonId, mode },
    });
    return data;
  },
  reviewCard: async (flashcardId, rating) => {
    const { data } = await apiClient.post(`/flashcards/${flashcardId}/review`, { rating });
    return data;
  },
};

export const analyticsApi = {
  getAnalytics: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/analytics`);
    return data;
  },
  getRecommendations: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/recommendations`);
    return data;
  },
  getUserAchievements: async () => {
    const { data } = await apiClient.get('/user/achievements');
    return data;
  },
  exportSummary: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/export`);
    return data;
  },
};

export const plannerApi = {
  getSchedule: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/planner`);
    return data;
  },
  updatePlan: async (courseId, planData) => {
    const { data } = await apiClient.post(`/courses/${courseId}/planner`, planData);
    return data;
  },
  getCalendar: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/calendar`);
    return data;
  },
  getPredictions: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/predictions`);
    return data;
  },
};

export const coachApi = {
  getAdvice: async (courseId = null) => {
    const { data } = await apiClient.get('/coach/advice', { params: { course_id: courseId } });
    return data;
  },
  getHabits: async (courseId) => {
    const { data } = await apiClient.get(`/coach/habits/${courseId}`);
    return data;
  },
};

export const notificationsApi = {
  getNotifications: async (priority = null) => {
    const { data } = await apiClient.get('/notifications', { params: { priority } });
    return data;
  },
  markRead: async (id) => {
    const { data } = await apiClient.post(`/notifications/${id}/read`);
    return data;
  },
};

export const reportsApi = {
  getWeeklyReport: async (courseId) => {
    const { data } = await apiClient.get(`/courses/${courseId}/weekly-report`);
    return data;
  },
};



