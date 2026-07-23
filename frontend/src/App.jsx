/**
 * CourseForge AI — Root Application Component
 *
 * Responsibilities:
 *  - Provide React Query client (server-state caching)
 *  - Provide React Router (client-side routing)
 *  - Render the route tree
 *
 * Phase 1: Renders a minimal working shell that confirms the app starts.
 * Phase 2: Routes to auth, dashboard, courses, learn, quiz, chat, flashcards,
 *           analytics, search, settings, and 404 pages.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import AppRouter from '@/router'
import { ToastContainer } from '@/components/ui/Toast'
import { ErrorBoundary } from '@/components/ui/ErrorBoundary'

/**
 * Global React Query client.
 *
 * Configuration:
 *  - staleTime: 60s — data is considered fresh for 1 minute
 *  - retry: 1    — retry failed queries once before showing error
 *  - refetchOnWindowFocus: false — avoids unexpected refetches
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppRouter />
          <ToastContainer />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}
