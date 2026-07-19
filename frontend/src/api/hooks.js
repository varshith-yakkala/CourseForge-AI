import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  coursesApi,
  documentsApi,
  searchApi,
  lessonsApi,
  quizzesApi,
  flashcardsApi,
  analyticsApi,
  plannerApi,
  coachApi,
  notificationsApi,
  reportsApi,
} from './services';

// Course Hooks
export const useCourses = () => {
  return useQuery({
    queryKey: ['courses'],
    queryFn: coursesApi.getAll,
    // Poll every 5s if any course is processing
    refetchInterval: (query) => {
      const isProcessing = query.state?.data?.some(c => c.status === 'processing' || c.status === 'generating_outline');
      return isProcessing ? 5000 : false;
    }
  });
};

export const useCourse = (id) => {
  return useQuery({
    queryKey: ['courses', id],
    queryFn: () => coursesApi.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      return (query.state?.data?.status === 'processing' || query.state?.data?.status === 'generating_outline') ? 3000 : false;
    }
  });
};

export const useCreateCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useDeleteCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useGenerateCourse = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: coursesApi.generate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['courses', data.id] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

export const useCourseStructure = (id) => {
  return useQuery({
    queryKey: ['courses', id, 'structure'],
    queryFn: () => coursesApi.getStructure(id),
    enabled: !!id,
  });
};

// Document Hooks
export const useUploadDocument = () => {
  return useMutation({
    mutationFn: ({ courseId, file, onUploadProgress }) => 
      documentsApi.upload(courseId, file, onUploadProgress),
  });
};

export const useCourseDocument = (courseId) => {
  return useQuery({
    queryKey: ['documents', 'course', courseId],
    queryFn: () => documentsApi.getByCourseId(courseId),
    enabled: !!courseId,
    refetchInterval: (query) => {
      return query.state?.data?.index_status === 'processing' || query.state?.data?.index_status === 'pending' ? 3000 : false;
    }
  });
};

export const useDocument = (id) => {
  return useQuery({
    queryKey: ['documents', id],
    queryFn: () => documentsApi.getById(id),
    enabled: !!id,
    refetchInterval: (query) => {
      return query.state?.data?.index_status === 'processing' || query.state?.data?.index_status === 'pending' ? 3000 : false;
    }
  });
};

export const useRetryDocument = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: documentsApi.retry,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['documents', data.id] });
      queryClient.invalidateQueries({ queryKey: ['courses'] });
    },
  });
};

// Search Hooks
export const useSearch = () => {
  return useMutation({
    mutationFn: ({ query, courseId }) => searchApi.search(query, courseId),
  });
};

// Phase 7: Lesson Hooks
export const useLesson = (courseId, lessonId) => {
  return useQuery({
    queryKey: ['lessons', courseId, lessonId],
    queryFn: () => lessonsApi.getLesson(courseId, lessonId),
    enabled: !!courseId && !!lessonId,
    refetchInterval: (query) => {
      const status = query.state?.data?.status;
      return (status === 'generating' || status === 'pending') ? 2500 : false;
    },
  });
};

export const useRegenerateLesson = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ courseId, lessonId }) => lessonsApi.regenerate(courseId, lessonId),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['lessons', variables.courseId, variables.lessonId] });
    },
  });
};

export const useUpdateProgress = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ courseId, lessonId, progressData }) =>
      lessonsApi.updateProgress(courseId, lessonId, progressData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['progress', variables.courseId] });
      queryClient.invalidateQueries({ queryKey: ['analytics', variables.courseId] });
      queryClient.invalidateQueries({ queryKey: ['planner', variables.courseId] });
    },
  });
};

export const useCourseProgress = (courseId) => {
  return useQuery({
    queryKey: ['progress', courseId],
    queryFn: () => lessonsApi.getCourseProgress(courseId),
    enabled: !!courseId,
  });
};

export const useAskLessonTutor = () => {
  return useMutation({
    mutationFn: ({ courseId, lessonId, question }) =>
      lessonsApi.askTutor(courseId, lessonId, question),
  });
};

// Phase 8: Quiz Hooks
export const useQuiz = (courseId, lessonId, difficulty = 'Intermediate', numQuestions = 10) => {
  return useQuery({
    queryKey: ['quizzes', courseId, lessonId, difficulty],
    queryFn: () => quizzesApi.getQuiz(courseId, lessonId, difficulty, numQuestions),
    enabled: !!courseId && !!lessonId,
  });
};

export const useSubmitQuiz = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ quizId, attemptData }) => quizzesApi.submitAttempt(quizId, attemptData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
      queryClient.invalidateQueries({ queryKey: ['planner'] });
    },
  });
};

// Phase 8: Flashcard Hooks
export const useFlashcards = (courseId, lessonId = null, mode = 'all') => {
  return useQuery({
    queryKey: ['flashcards', courseId, lessonId, mode],
    queryFn: () => flashcardsApi.getDeck(courseId, lessonId, mode),
    enabled: !!courseId,
  });
};

export const useReviewFlashcard = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ flashcardId, rating }) => flashcardsApi.reviewCard(flashcardId, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
      queryClient.invalidateQueries({ queryKey: ['analytics'] });
    },
  });
};

// Phase 8: Analytics & Export Hooks
export const useAnalytics = (courseId) => {
  return useQuery({
    queryKey: ['analytics', courseId],
    queryFn: () => analyticsApi.getAnalytics(courseId),
    enabled: !!courseId,
  });
};

export const useRecommendations = (courseId) => {
  return useQuery({
    queryKey: ['recommendations', courseId],
    queryFn: () => analyticsApi.getRecommendations(courseId),
    enabled: !!courseId,
  });
};

export const useUserAchievements = () => {
  return useQuery({
    queryKey: ['achievements'],
    queryFn: analyticsApi.getUserAchievements,
  });
};

export const useExportSummary = (courseId) => {
  return useQuery({
    queryKey: ['export', courseId],
    queryFn: () => analyticsApi.exportSummary(courseId),
    enabled: false,
  });
};

// Phase 9: Planner, Calendar, Predictions, Coach, Notifications, Reports Hooks
export const usePlannerSchedule = (courseId) => {
  return useQuery({
    queryKey: ['planner', courseId],
    queryFn: () => plannerApi.getSchedule(courseId),
    enabled: !!courseId,
  });
};

export const useUpdatePlannerPlan = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ courseId, planData }) => plannerApi.updatePlan(courseId, planData),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['planner', variables.courseId] });
      queryClient.invalidateQueries({ queryKey: ['calendar', variables.courseId] });
    },
  });
};

export const useCalendarEvents = (courseId) => {
  return useQuery({
    queryKey: ['calendar', courseId],
    queryFn: () => plannerApi.getCalendar(courseId),
    enabled: !!courseId,
  });
};

export const usePredictions = (courseId) => {
  return useQuery({
    queryKey: ['predictions', courseId],
    queryFn: () => plannerApi.getPredictions(courseId),
    enabled: !!courseId,
  });
};

export const useCoachAdvice = (courseId = null) => {
  return useQuery({
    queryKey: ['coach', courseId],
    queryFn: () => coachApi.getAdvice(courseId),
  });
};

export const useHabits = (courseId) => {
  return useQuery({
    queryKey: ['habits', courseId],
    queryFn: () => coachApi.getHabits(courseId),
    enabled: !!courseId,
  });
};

export const useNotifications = (priority = null) => {
  return useQuery({
    queryKey: ['notifications', priority],
    queryFn: () => notificationsApi.getNotifications(priority),
    refetchInterval: 10000, // Refresh notifications every 10s
  });
};

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => notificationsApi.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useWeeklyReport = (courseId) => {
  return useQuery({
    queryKey: ['weeklyReport', courseId],
    queryFn: () => reportsApi.getWeeklyReport(courseId),
    enabled: !!courseId,
  });
};



