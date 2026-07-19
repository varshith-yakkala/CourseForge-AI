/**
 * CourseForge AI — Application Router
 *
 * Defines all client-side routes using React Router v6.
 *
 * Phase 1: Minimal working routes — home redirect, 404.
 * Phase 2: Auth routes (login, register).
 * Phase 3: App routes (dashboard, courses, learn, quiz, chat, flashcards,
 *           analytics, search, settings).
 *
 * Route structure:
 *   /                     → redirect to /dashboard (if authed) or /login
 *   /login                → LoginPage
 *   /register             → RegisterPage
 *   /dashboard            → DashboardPage        [requires auth]
 *   /courses              → CoursesPage          [requires auth]
 *   /courses/:id          → CourseDetailPage      [requires auth]
 *   /learn/:courseId/:topicId → LearnPage         [requires auth]
 *   /quiz/:quizId         → QuizPage             [requires auth]
 *   /quiz/:quizId/result  → QuizResultPage       [requires auth]
 *   /chat                 → ChatPage             [requires auth]
 *   /flashcards/:courseId → FlashcardsPage       [requires auth]
 *   /search               → SearchPage           [requires auth]
 *   /analytics            → AnalyticsPage        [requires auth]
 *   /settings             → SettingsPage         [requires auth]
 *   *                     → NotFoundPage
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';

// Layouts
import { AppLayout } from '@/components/layout/AppLayout';

// Pages
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';
import DashboardPage from '@/pages/DashboardPage';
import CoursesPage from '@/pages/CoursesPage';
import CourseDetailPage from '@/pages/CourseDetailPage';
import LessonViewerPage from '@/pages/LessonViewerPage';
import QuizPage from '@/pages/QuizPage';
import ChatPage from '@/pages/ChatPage';
import AnalyticsPage from '@/pages/AnalyticsPage';
import SettingsPage from '@/pages/SettingsPage';
import NotFoundPage from '@/pages/NotFoundPage';

import FlashcardsPage from '@/pages/FlashcardsPage';
import StudyPlannerPage from '@/pages/StudyPlannerPage';
import CalendarPage from '@/pages/CalendarPage';
import WeeklyReportPage from '@/pages/WeeklyReportPage';

function ProtectedRoute({ children }) {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function GuestRoute({ children }) {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

export default function AppRouter() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<GuestRoute><LandingPage /></GuestRoute>} />
      <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
      <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />

      {/* Protected App Routes with Sidebar/TopNav Layout */}
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/courses" element={<CoursesPage />} />
        <Route path="/courses/:id" element={<CourseDetailPage />} />
        <Route path="/learn/:courseId/:lessonId" element={<LessonViewerPage />} />
        <Route path="/learn/:courseId" element={<LessonViewerPage />} />
        <Route path="/quiz/:courseId/:lessonId" element={<QuizPage />} />
        <Route path="/quiz/:quizId" element={<QuizPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/flashcards/:courseId" element={<FlashcardsPage />} />
        <Route path="/analytics/:courseId" element={<AnalyticsPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/planner/:courseId" element={<StudyPlannerPage />} />
        <Route path="/calendar/:courseId" element={<CalendarPage />} />
        <Route path="/weekly-report/:courseId" element={<WeeklyReportPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

