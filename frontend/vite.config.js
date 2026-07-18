import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

/**
 * Vite configuration for CourseForge AI frontend.
 *
 * Key configuration:
 *  - Path alias @/ resolves to src/ for clean imports
 *  - Dev proxy: /api/* → FastAPI backend (avoids CORS in dev)
 *  - Build: chunk splitting for better caching
 *  - Test: jsdom environment with Testing Library globals
 */
export default defineConfig({
  plugins: [
    react(),
  ],

  // ─────────────────────────────────────────────
  // Path aliases — import from @/components/... instead of ../../components/...
  // ─────────────────────────────────────────────
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // ─────────────────────────────────────────────
  // Dev server configuration
  // ─────────────────────────────────────────────
  server: {
    port: 5173,
    host: true,
    proxy: {
      // Proxy all /api requests to FastAPI in development
      // This eliminates CORS issues during local development
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        ws: true,    // WebSocket proxying for real-time generation updates
      },
    },
  },

  // ─────────────────────────────────────────────
  // Build configuration
  // ─────────────────────────────────────────────
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    target: 'es2020',
    rollupOptions: {
      output: {
        // Manual chunk splitting for vendor libraries (better CDN caching)
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'ui-vendor': ['recharts', 'lucide-react'],
          'utils-vendor': ['axios', 'zustand', 'clsx', 'date-fns'],
        },
      },
    },
  },

  // ─────────────────────────────────────────────
  // Vitest test configuration
  // ─────────────────────────────────────────────
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/**/*.{js,jsx}'],
      exclude: [
        'src/test/**',
        'src/**/*.test.{js,jsx}',
        'src/main.jsx',
      ],
      thresholds: {
        lines: 60,
        functions: 60,
        branches: 60,
      },
    },
  },
})
