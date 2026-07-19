# Changelog — CourseForge AI

All notable changes to the CourseForge AI project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-07-19

### 🚀 Production Hardening & Official v1.0.0 Release

#### Added
- **Multi-Stage Dockerization**: Production `Dockerfile` for backend and frontend, and root `docker-compose.yml` orchestrating PostgreSQL 15, Redis 7, Celery Worker, FastAPI, and Nginx.
- **Security Headers Middleware**: Enforced `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Content-Security-Policy`, and CORS origin validation.
- **Request Tracing**: `X-Request-ID` header injection and propagation across request logs and Celery tasks.
- **Health & Readiness Endpoints**: Added `/health` (liveness), `/ready` (DB, Redis, Celery, InsightForge readiness), and `/metrics` (CPU, Memory, Uptime).
- **Personalized Learning Intelligence (Phase 9)**: Adaptive Study Planner, Multi-Event Learning Calendar, Learning Pace Predictions, Habit Heatmap Grid, Proactive AI Learning Coach widget, Priority Smart Notifications, and AI Weekly Report.
- **Assessment & Reinforcement Engine (Phase 8)**: Adaptive Difficulty Quizzes, Pool Sampling, Partial Credit, 3D Flashcard Reader, SuperMemo SM-2 Spaced Repetition, and Gamification Badges.
- **Interactive AI Lessons (Phase 7)**: Markdown Lesson Generator, Lesson Lifecycle, AI Tutor, and Versioning.

#### Changed
- Upgraded repository structure, documentation, and error handling for production readiness.
- Standardized API JSON error responses with `request_id` and timestamps.

---

## [0.8.0] — 2026-07-19

### 🧠 Assessment Engine & Flashcards
- Implemented SuperMemo SM-2 algorithm.
- Added adaptive quiz generator with difficulty selection.
- Added learning analytics dashboard and weak topic identification.

---

## [0.7.0] — 2026-07-19

### 📚 Interactive Lessons & AI Tutor
- Added on-demand AI lesson generation.
- Added AI Lesson Tutor sidebar for in-lesson Q&A.
- Added lesson progress tracking and version history.
