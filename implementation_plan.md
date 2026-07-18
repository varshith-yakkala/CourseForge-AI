# CourseForge AI — Complete Software Design Package

> **Version:** 1.0 — Architecture Freeze Document  
> **Author:** Principal Software Architect  
> **Date:** 2026-07-18  
> **Status:** Awaiting User Approval Before Code Begins  

---

## Preface

This document is the **single source of truth** for CourseForge AI. Every design decision is made here so that no table, API, folder, or component ever needs to be redesigned during implementation. Read every section before writing a single line of code.

**InsightForge-AI** (located at `C:\Users\varsh\OneDrive\Desktop\2-2\aiforage\InsightForge-AI`) is treated as a **stable internal AI engine**. CourseForge wraps it — never duplicates it.

**InsightForge confirmed capabilities (from code review):**
- `IndexingPipeline` — PDF/Text/Markdown loader → CharacterChunker → FAISS + BM25 index
- `QueryPipeline` — Retrieve → CrossEncoder Rerank → Context Compress → Confidence → Groq LLM (llama-3.3-70b)
- `HybridRetriever` — Semantic (FAISS cosine) + BM25 fusion scoring
- `RAGService` — Thin orchestrator over Indexing + Query
- `EmbeddingService` — sentence-transformers/all-MiniLM-L6-v2
- API routes: `GET /health`, `GET /documents`, `GET /documents/{id}`, `GET /stats`, `POST /upload`, `POST /query`

---

# SECTION 1 — SYSTEM ARCHITECTURE

## 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                │
│          React + Vite + TailwindCSS (SPA)                          │
└───────────────────────┬─────────────────────────────────────────────┘
                        │ HTTPS / REST / WebSocket
┌───────────────────────▼─────────────────────────────────────────────┐
│              COURSEFORGE API GATEWAY (FastAPI)                      │
│   Auth │ Courses │ Lessons │ Quiz │ Chat │ Progress │ Analytics     │
│              CourseForge Backend — Port 8001                        │
└──────┬──────────────────────┬──────────────────────────────────────┘
       │ Internal Python call  │ Background Job Queue (Celery + Redis)
       │                       │
┌──────▼──────┐     ┌─────────▼──────────────────────────────────────┐
│ PostgreSQL  │     │          INSIGHTFORGE-AI ENGINE                 │
│ (Primary DB)│     │   IndexingPipeline │ QueryPipeline              │
│             │     │   HybridRetriever  │ RAGService                 │
│ Redis Cache │     │   EmbeddingService │ FAISSStore + BM25          │
│             │     │   Groq LLM (llama-3.3-70b)                     │
└─────────────┘     └────────────────────────────────────────────────┘
```

**Layers:**
| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18 + Vite + Vanilla CSS | SPA, all UI screens |
| API Gateway | FastAPI (Python 3.11) | REST API, JWT auth, routing |
| Background Jobs | Celery + Redis | Async course generation, exports |
| Primary Database | PostgreSQL 15 | All relational data |
| Cache | Redis 7 | Sessions, job status, query cache |
| AI Engine | InsightForge-AI (internal) | RAG, embeddings, LLM |
| File Storage | Local filesystem (S3-ready) | PDF uploads, exports |

---

## 1.2 Detailed Architecture

```
CourseForge Backend (FastAPI)
├── api/
│   ├── auth/         JWT issue, refresh, revoke
│   ├── courses/      CRUD + generation trigger
│   ├── lessons/      lesson + topic CRUD
│   ├── quiz/         generation + submission
│   ├── chat/         AI tutor session management
│   ├── progress/     read/update progress events
│   ├── search/       semantic + keyword search
│   ├── analytics/    usage metrics
│   ├── flashcards/   CRUD + spaced repetition
│   ├── export/       PDF/Markdown export trigger
│   └── notifications/ alert management
├── services/
│   ├── course_generator.py     ← calls InsightForge
│   ├── quiz_generator.py       ← calls InsightForge
│   ├── chat_service.py         ← calls InsightForge
│   ├── flashcard_generator.py  ← calls InsightForge
│   ├── revision_service.py     ← calls InsightForge
│   ├── search_service.py       ← calls InsightForge
│   ├── export_service.py       ← renders PDF/Markdown
│   └── analytics_service.py   ← aggregates DB data
├── tasks/
│   ├── generate_course_task.py
│   ├── generate_quiz_task.py
│   └── export_task.py
├── db/
│   ├── models/       SQLAlchemy ORM models
│   ├── migrations/   Alembic versions
│   └── session.py
├── core/
│   ├── config.py
│   ├── security.py   JWT + bcrypt
│   └── exceptions.py
└── insightforge/
    └── engine.py     ← InsightForge adapter (THE integration layer)
```

---

## 1.3 Data Flow Diagrams

### Upload & Course Generation Flow
```
User uploads PDF
      │
      ▼
POST /api/v1/courses/upload
      │
      ▼
CourseForge saves file to /uploads/{user_id}/{course_id}/
      │
      ▼
Celery Task: generate_course_task(course_id, file_path)
      │
      ├── Step 1: InsightForge.index(file_path)
      │           └── Loader → Chunker → Embedder → FAISS + BM25
      │
      ├── Step 2: course_generator.generate_structure(course_id)
      │           └── QueryPipeline.query("Extract course structure...")
      │           └── JSON parse → Lessons → Topics → Subtopics
      │
      ├── Step 3: course_generator.generate_lessons(course_id)
      │           └── For each topic → QueryPipeline.query(topic)
      │           └── Save to DB: lessons, topics, subtopics
      │
      ├── Step 4: quiz_generator.generate(course_id)
      │           └── For each lesson → generate MCQ + TF + open-ended
      │
      ├── Step 5: flashcard_generator.generate(course_id)
      │           └── Key concepts → front/back flashcards
      │
      └── Step 6: Update course status = "ready"
                  Emit WebSocket event to user
```

### Chat (AI Tutor) Flow
```
User asks question in chat
      │
      ▼
POST /api/v1/chat/message
      │
      ▼
ChatService.handle(session_id, user_message)
      │
      ├── Load chat history from DB (last 10 turns)
      ├── Build context-aware prompt with history
      ├── InsightForge.QueryPipeline.query(question)
      │       └── Retrieves chunks from course-specific FAISS namespace
      ├── Attach sources + confidence to response
      ├── Save to chat_messages table
      └── Return {answer, sources, confidence, citations}
```

### Quiz Flow
```
User starts quiz for a lesson
      │
      ▼
POST /api/v1/quiz/{quiz_id}/attempt
      │
      ├── Load questions from quiz_questions table
      ├── Shuffle questions (configurable)
      ├── Return QuizSession {attempt_id, questions}
      │
User submits answers
      │
      ▼
POST /api/v1/quiz/attempts/{attempt_id}/submit
      │
      ├── Grade each answer
      ├── Calculate score, time_taken, per-question result
      ├── Save to quiz_attempts + quiz_attempt_answers
      ├── Update progress table
      └── Return {score, passed, results, explanations}
```

### Search Flow
```
User types search query
      │
      ▼
GET /api/v1/search?q=...&course_id=...
      │
      ├── SearchService.search(query, course_id)
      │       ├── InsightForge.HybridRetriever.retrieve(query, top_k=10)
      │       │       └── Filter by document_id belonging to course
      │       ├── Keyword search against lesson titles in PostgreSQL
      │       └── Merge + deduplicate results
      │
      └── Return {lessons, topics, chunks, sources}
```

### Progress Flow
```
User completes a lesson / quiz / flashcard
      │
      ▼
POST /api/v1/progress/event
      │
      ├── Insert into user_progress table
      ├── Check if all lessons in a course completed → update course_enrollments
      ├── Check certificate eligibility (score >= threshold)
      └── Return updated {course_progress_pct, lesson_status}
```

---

# SECTION 2 — COMPLETE PROJECT FOLDER STRUCTURE

```
CourseForge-AI/
│
├── backend/                            # FastAPI Python backend
│   ├── main.py                         # FastAPI app entrypoint
│   ├── requirements.txt
│   │
│   ├── api/                            # All route handlers
│   │   ├── __init__.py
│   │   ├── deps.py                     # Shared dependencies (get_db, get_current_user)
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py               # /auth/register, /login, /refresh, /logout
│   │   │   └── schemas.py
│   │   ├── courses/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── lessons/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── quiz/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── chat/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── progress/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── search/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── flashcards/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── analytics/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── export/
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── notifications/
│   │       ├── routes.py
│   │       └── schemas.py
│   │
│   ├── services/                       # Business logic
│   │   ├── course_generator.py
│   │   ├── quiz_generator.py
│   │   ├── chat_service.py
│   │   ├── flashcard_generator.py
│   │   ├── revision_service.py
│   │   ├── search_service.py
│   │   ├── export_service.py
│   │   └── analytics_service.py
│   │
│   ├── tasks/                          # Celery background jobs
│   │   ├── celery_app.py
│   │   ├── generate_course_task.py
│   │   ├── generate_quiz_task.py
│   │   └── export_task.py
│   │
│   ├── db/                             # Database layer
│   │   ├── session.py                  # SQLAlchemy engine + session
│   │   ├── base.py                     # Declarative base
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── course.py
│   │   │   ├── document.py
│   │   │   ├── lesson.py
│   │   │   ├── topic.py
│   │   │   ├── subtopic.py
│   │   │   ├── enrollment.py
│   │   │   ├── progress.py
│   │   │   ├── quiz.py
│   │   │   ├── quiz_question.py
│   │   │   ├── quiz_attempt.py
│   │   │   ├── quiz_attempt_answer.py
│   │   │   ├── flashcard.py
│   │   │   ├── flashcard_review.py
│   │   │   ├── chat_session.py
│   │   │   ├── chat_message.py
│   │   │   ├── analytics_event.py
│   │   │   ├── notification.py
│   │   │   ├── bookmark.py
│   │   │   └── certificate.py
│   │   └── migrations/
│   │       └── versions/
│   │
│   ├── core/
│   │   ├── config.py                   # Pydantic Settings
│   │   ├── security.py                 # JWT, bcrypt
│   │   ├── exceptions.py
│   │   └── middleware.py               # CORS, logging
│   │
│   ├── insightforge/                   # THE integration layer
│   │   ├── __init__.py
│   │   ├── engine.py                   # InsightForgeEngine class
│   │   ├── adapter.py                  # Namespace-aware query adapter
│   │   └── config.py                   # Path to InsightForge project
│   │
│   └── prompts/                        # Versioned prompt templates
│       ├── v1/
│       │   ├── course_structure.txt
│       │   ├── lesson_content.txt
│       │   ├── quiz_mcq.txt
│       │   ├── quiz_tf.txt
│       │   ├── quiz_open.txt
│       │   ├── flashcard.txt
│       │   ├── chat_tutor.txt
│       │   └── revision_summary.txt
│       └── prompt_manager.py
│
├── frontend/                           # React + Vite frontend
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css                   # Design tokens + global styles
│   │   │
│   │   ├── assets/                     # Fonts, images, icons
│   │   │
│   │   ├── api/                        # Axios client + all API hooks
│   │   │   ├── client.js               # Axios instance + interceptors
│   │   │   ├── auth.js
│   │   │   ├── courses.js
│   │   │   ├── lessons.js
│   │   │   ├── quiz.js
│   │   │   ├── chat.js
│   │   │   ├── progress.js
│   │   │   ├── search.js
│   │   │   ├── flashcards.js
│   │   │   ├── analytics.js
│   │   │   ├── export.js
│   │   │   └── notifications.js
│   │   │
│   │   ├── store/                      # Zustand global state
│   │   │   ├── authStore.js
│   │   │   ├── courseStore.js
│   │   │   ├── chatStore.js
│   │   │   ├── progressStore.js
│   │   │   ├── quizStore.js
│   │   │   ├── searchStore.js
│   │   │   └── uiStore.js              # Sidebar, modal, theme
│   │   │
│   │   ├── hooks/                      # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useCourse.js
│   │   │   ├── useChat.js
│   │   │   ├── useProgress.js
│   │   │   ├── useQuiz.js
│   │   │   ├── useSearch.js
│   │   │   ├── useFlashcards.js
│   │   │   └── useWebSocket.js
│   │   │
│   │   ├── components/                 # Reusable UI components
│   │   │   ├── ui/                     # Atomic design system
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── Badge.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Tooltip.jsx
│   │   │   │   ├── Spinner.jsx
│   │   │   │   ├── Progress.jsx
│   │   │   │   ├── Tabs.jsx
│   │   │   │   ├── Avatar.jsx
│   │   │   │   ├── Dropdown.jsx
│   │   │   │   ├── Toast.jsx
│   │   │   │   └── EmptyState.jsx
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.jsx       # Shell: sidebar + topbar + content
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── Topbar.jsx
│   │   │   │   └── AuthLayout.jsx
│   │   │   ├── course/
│   │   │   │   ├── CourseCard.jsx
│   │   │   │   ├── CourseGrid.jsx
│   │   │   │   ├── LessonList.jsx
│   │   │   │   ├── LessonViewer.jsx
│   │   │   │   ├── TopicTree.jsx
│   │   │   │   └── CourseProgress.jsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.jsx
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   └── SourceCitation.jsx
│   │   │   ├── quiz/
│   │   │   │   ├── QuizCard.jsx
│   │   │   │   ├── QuizQuestion.jsx
│   │   │   │   ├── QuizResult.jsx
│   │   │   │   └── QuizTimer.jsx
│   │   │   ├── flashcard/
│   │   │   │   ├── FlashcardDeck.jsx
│   │   │   │   └── FlashcardFlip.jsx
│   │   │   ├── search/
│   │   │   │   ├── SearchBar.jsx
│   │   │   │   └── SearchResults.jsx
│   │   │   ├── analytics/
│   │   │   │   ├── ProgressChart.jsx
│   │   │   │   └── ActivityHeatmap.jsx
│   │   │   └── upload/
│   │   │       ├── UploadZone.jsx
│   │   │       └── UploadProgress.jsx
│   │   │
│   │   ├── pages/                      # Route-level page components
│   │   │   ├── auth/
│   │   │   │   ├── LoginPage.jsx
│   │   │   │   └── RegisterPage.jsx
│   │   │   ├── dashboard/
│   │   │   │   └── DashboardPage.jsx
│   │   │   ├── courses/
│   │   │   │   ├── CoursesPage.jsx
│   │   │   │   ├── CourseDetailPage.jsx
│   │   │   │   └── CreateCoursePage.jsx
│   │   │   ├── learn/
│   │   │   │   └── LearnPage.jsx
│   │   │   ├── quiz/
│   │   │   │   ├── QuizPage.jsx
│   │   │   │   └── QuizResultPage.jsx
│   │   │   ├── chat/
│   │   │   │   └── ChatPage.jsx
│   │   │   ├── flashcards/
│   │   │   │   └── FlashcardsPage.jsx
│   │   │   ├── search/
│   │   │   │   └── SearchPage.jsx
│   │   │   ├── analytics/
│   │   │   │   └── AnalyticsPage.jsx
│   │   │   ├── settings/
│   │   │   │   └── SettingsPage.jsx
│   │   │   └── NotFoundPage.jsx
│   │   │
│   │   └── router/
│   │       └── index.jsx               # React Router v6 routes
│   │
│   └── public/
│       └── favicon.ico
│
├── uploads/                            # User-uploaded PDF files
│   └── {user_id}/
│       └── {course_id}/
│           └── original.pdf
│
├── exports/                            # Generated export files
│   └── {user_id}/
│       └── {course_id}/
│           ├── course.pdf
│           └── course.md
│
├── tests/
│   ├── backend/
│   │   ├── unit/
│   │   │   ├── test_course_generator.py
│   │   │   ├── test_quiz_generator.py
│   │   │   └── test_chat_service.py
│   │   ├── integration/
│   │   │   ├── test_upload_flow.py
│   │   │   ├── test_course_generation.py
│   │   │   └── test_auth.py
│   │   └── conftest.py
│   └── frontend/
│       ├── components/
│       └── pages/
│
├── docs/
│   ├── architecture.md                 # This document
│   ├── api_reference.md
│   ├── insightforge_integration.md
│   └── deployment.md
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── scripts/
│   ├── seed_db.py
│   ├── migrate.py
│   └── start_dev.sh
│
├── .env.example
├── .gitignore
└── README.md
```

---

# SECTION 3 — DATABASE DESIGN

## Technology: PostgreSQL 15 with SQLAlchemy ORM + Alembic migrations

**Design Principles:**
- Every table has UUID primary keys (future-proof, safe for distributed systems)
- Every table has `created_at` and `updated_at` timestamps (automatic via triggers)
- All foreign keys have explicit `ON DELETE` behavior
- Soft deletes via `deleted_at` on mutable entities (users, courses)
- Status columns use string enums, not integers, for readability

---

### Table: `users`
**Why:** Stores all registered users. Central entity for auth, ownership, and analytics.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Login identifier |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hash |
| `full_name` | VARCHAR(255) | NOT NULL | |
| `avatar_url` | TEXT | NULLABLE | Profile picture |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT 'student' | 'student' \| 'admin' |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Account enabled |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT false | Email verified |
| `last_login_at` | TIMESTAMPTZ | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `deleted_at` | TIMESTAMPTZ | NULLABLE | Soft delete |

**Indexes:** `idx_users_email`, `idx_users_role`

---

### Table: `courses`
**Why:** Top-level container for a learning course generated from a PDF.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `owner_id` | UUID | FK → users.id ON DELETE CASCADE | Creator |
| `title` | VARCHAR(500) | NOT NULL | AI-generated or user-edited |
| `description` | TEXT | NULLABLE | AI-generated summary |
| `thumbnail_url` | TEXT | NULLABLE | Generated cover image |
| `status` | VARCHAR(30) | NOT NULL, DEFAULT 'processing' | 'processing' \| 'ready' \| 'failed' |
| `generation_error` | TEXT | NULLABLE | Error message if failed |
| `difficulty` | VARCHAR(20) | NULLABLE | 'beginner' \| 'intermediate' \| 'advanced' |
| `estimated_duration_min` | INTEGER | NULLABLE | AI-estimated reading time |
| `language` | VARCHAR(10) | NOT NULL, DEFAULT 'en' | ISO 639-1 |
| `is_public` | BOOLEAN | NOT NULL, DEFAULT false | Share toggle |
| `tags` | TEXT[] | NULLABLE | Searchable tags array |
| `created_at` | TIMESTAMPTZ | NOT NULL | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | |
| `deleted_at` | TIMESTAMPTZ | NULLABLE | Soft delete |

**Indexes:** `idx_courses_owner_id`, `idx_courses_status`, `idx_courses_tags` (GIN)

---

### Table: `documents`
**Why:** Tracks the original PDF file tied to each course. Decoupled so a course can reference one document, and the document tracks its InsightForge indexing state.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE, UNIQUE | 1-to-1 |
| `owner_id` | UUID | FK → users.id | |
| `original_filename` | VARCHAR(500) | NOT NULL | |
| `stored_path` | TEXT | NOT NULL | Filesystem path |
| `file_size_bytes` | BIGINT | NOT NULL | |
| `mime_type` | VARCHAR(100) | NOT NULL | |
| `page_count` | INTEGER | NULLABLE | Extracted on upload |
| `insightforge_doc_id` | VARCHAR(255) | NULLABLE, INDEX | ID from InsightForge registry |
| `index_status` | VARCHAR(30) | NOT NULL, DEFAULT 'pending' | 'pending' \| 'indexed' \| 'failed' |
| `chunk_count` | INTEGER | NULLABLE | From IndexingPipeline |
| `indexed_at` | TIMESTAMPTZ | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_documents_course_id`, `idx_documents_insightforge_doc_id`

---

### Table: `lessons`
**Why:** AI-generated top-level chapters of a course.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE, INDEX | |
| `title` | VARCHAR(500) | NOT NULL | |
| `summary` | TEXT | NULLABLE | AI one-paragraph summary |
| `order_index` | INTEGER | NOT NULL | Display order |
| `estimated_duration_min` | INTEGER | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_lessons_course_id`, composite `idx_lessons_course_order(course_id, order_index)`

---

### Table: `topics`
**Why:** Sub-sections within a lesson.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `lesson_id` | UUID | FK → lessons.id ON DELETE CASCADE, INDEX | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | For direct queries |
| `title` | VARCHAR(500) | NOT NULL | |
| `content` | TEXT | NOT NULL | Full AI-generated text |
| `order_index` | INTEGER | NOT NULL | |
| `key_terms` | TEXT[] | NULLABLE | Extracted keywords |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_topics_lesson_id`, `idx_topics_course_id`

---

### Table: `subtopics`
**Why:** Optional deeper nesting for complex PDFs.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `topic_id` | UUID | FK → topics.id ON DELETE CASCADE | |
| `lesson_id` | UUID | FK → lessons.id | For direct queries |
| `course_id` | UUID | FK → courses.id | |
| `title` | VARCHAR(500) | NOT NULL | |
| `content` | TEXT | NOT NULL | |
| `order_index` | INTEGER | NOT NULL | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_subtopics_topic_id`

---

### Table: `course_enrollments`
**Why:** Tracks which user is enrolled in which course and overall progress.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `enrolled_at` | TIMESTAMPTZ | NOT NULL | |
| `completed_at` | TIMESTAMPTZ | NULLABLE | |
| `progress_pct` | DECIMAL(5,2) | NOT NULL, DEFAULT 0 | 0.00–100.00 |
| `last_accessed_at` | TIMESTAMPTZ | NULLABLE | |

**Constraints:** `UNIQUE (user_id, course_id)`  
**Indexes:** `idx_enrollments_user_id`, `idx_enrollments_course_id`

---

### Table: `user_progress`
**Why:** Granular event log — which lesson/topic was completed by which user. Source of truth for progress calculation.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `lesson_id` | UUID | FK → lessons.id ON DELETE CASCADE, NULLABLE | |
| `topic_id` | UUID | FK → topics.id ON DELETE CASCADE, NULLABLE | |
| `entity_type` | VARCHAR(20) | NOT NULL | 'lesson' \| 'topic' \| 'quiz' \| 'flashcard' |
| `status` | VARCHAR(20) | NOT NULL | 'started' \| 'completed' |
| `time_spent_sec` | INTEGER | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_progress_user_course(user_id, course_id)`, `idx_progress_lesson_id`

---

### Table: `quizzes`
**Why:** A quiz is attached to a lesson. Stores metadata and configuration.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `lesson_id` | UUID | FK → lessons.id ON DELETE CASCADE, UNIQUE | 1-to-1 |
| `course_id` | UUID | FK → courses.id | |
| `title` | VARCHAR(500) | NOT NULL | |
| `pass_score_pct` | DECIMAL(5,2) | NOT NULL, DEFAULT 70.0 | |
| `time_limit_min` | INTEGER | NULLABLE | NULL = no limit |
| `max_attempts` | INTEGER | NOT NULL, DEFAULT 3 | |
| `shuffle_questions` | BOOLEAN | NOT NULL, DEFAULT true | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_quizzes_lesson_id`, `idx_quizzes_course_id`

---

### Table: `quiz_questions`
**Why:** Individual questions. Supports MCQ, True/False, and open-ended.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `quiz_id` | UUID | FK → quizzes.id ON DELETE CASCADE, INDEX | |
| `question_text` | TEXT | NOT NULL | |
| `question_type` | VARCHAR(20) | NOT NULL | 'mcq' \| 'true_false' \| 'open' |
| `options` | JSONB | NULLABLE | [{label, text, is_correct}] |
| `correct_answer` | TEXT | NOT NULL | For grading |
| `explanation` | TEXT | NULLABLE | Shown after submission |
| `difficulty` | VARCHAR(20) | NULLABLE | 'easy' \| 'medium' \| 'hard' |
| `order_index` | INTEGER | NOT NULL | |
| `source_chunk_ids` | TEXT[] | NULLABLE | InsightForge chunk IDs |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_quiz_questions_quiz_id`

---

### Table: `quiz_attempts`
**Why:** Each time a user attempts a quiz.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `quiz_id` | UUID | FK → quizzes.id ON DELETE CASCADE | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `started_at` | TIMESTAMPTZ | NOT NULL | |
| `submitted_at` | TIMESTAMPTZ | NULLABLE | |
| `score_pct` | DECIMAL(5,2) | NULLABLE | Calculated on submit |
| `passed` | BOOLEAN | NULLABLE | |
| `time_taken_sec` | INTEGER | NULLABLE | |
| `attempt_number` | INTEGER | NOT NULL | 1, 2, 3 … |

**Indexes:** `idx_quiz_attempts_user_quiz(user_id, quiz_id)`, `idx_quiz_attempts_quiz_id`

---

### Table: `quiz_attempt_answers`
**Why:** Per-question answer record for each attempt. Enables detailed review.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `attempt_id` | UUID | FK → quiz_attempts.id ON DELETE CASCADE | |
| `question_id` | UUID | FK → quiz_questions.id | |
| `user_answer` | TEXT | NOT NULL | |
| `is_correct` | BOOLEAN | NOT NULL | |
| `time_spent_sec` | INTEGER | NULLABLE | |

**Indexes:** `idx_attempt_answers_attempt_id`

---

### Table: `flashcards`
**Why:** Key concept cards with front (term) and back (definition), generated from course content.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `lesson_id` | UUID | FK → lessons.id ON DELETE SET NULL, NULLABLE | |
| `front` | TEXT | NOT NULL | Term / concept |
| `back` | TEXT | NOT NULL | Definition / explanation |
| `source_chunk_ids` | TEXT[] | NULLABLE | Traceability |
| `order_index` | INTEGER | NOT NULL | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_flashcards_course_id`, `idx_flashcards_lesson_id`

---

### Table: `flashcard_reviews`
**Why:** Spaced repetition state per user per flashcard.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `flashcard_id` | UUID | FK → flashcards.id ON DELETE CASCADE | |
| `rating` | VARCHAR(10) | NOT NULL | 'again' \| 'hard' \| 'good' \| 'easy' |
| `next_review_at` | TIMESTAMPTZ | NOT NULL | SM-2 algorithm output |
| `interval_days` | INTEGER | NOT NULL, DEFAULT 1 | |
| `ease_factor` | DECIMAL(4,2) | NOT NULL, DEFAULT 2.5 | |
| `reviewed_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_flashcard_reviews_user_card(user_id, flashcard_id)`, `idx_flashcard_reviews_next_review`

---

### Table: `chat_sessions`
**Why:** Logical grouping of a conversation between user and AI tutor within a course.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `title` | VARCHAR(500) | NULLABLE | Auto-generated from first message |
| `created_at` | TIMESTAMPTZ | NOT NULL | |
| `updated_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_chat_sessions_user_course(user_id, course_id)`

---

### Table: `chat_messages`
**Why:** Individual messages in a chat session. Stores role, content, sources.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `session_id` | UUID | FK → chat_sessions.id ON DELETE CASCADE, INDEX | |
| `role` | VARCHAR(20) | NOT NULL | 'user' \| 'assistant' |
| `content` | TEXT | NOT NULL | |
| `sources` | JSONB | NULLABLE | [{filename, page, chunk_id, similarity}] |
| `confidence` | DECIMAL(4,3) | NULLABLE | 0.000–1.000 |
| `generation_time_ms` | INTEGER | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_chat_messages_session_id`

---

### Table: `analytics_events`
**Why:** Append-only event log for all user actions. Powers the analytics dashboard.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE SET NULL, NULLABLE | |
| `event_type` | VARCHAR(50) | NOT NULL | 'page_view' \| 'lesson_start' \| 'lesson_complete' \| 'quiz_start' \| 'quiz_pass' \| 'chat_message' \| 'search' \| 'flashcard_review' |
| `metadata` | JSONB | NULLABLE | Flexible event data |
| `session_id` | VARCHAR(255) | NULLABLE | Browser session |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_analytics_user_id`, `idx_analytics_course_id`, `idx_analytics_event_type`, `idx_analytics_created_at`  
> **Note:** This table is append-only. Never update or delete rows. Partition by `created_at` monthly in production.

---

### Table: `notifications`
**Why:** In-app notifications (course ready, quiz passed, certificate earned).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `type` | VARCHAR(50) | NOT NULL | 'course_ready' \| 'quiz_result' \| 'certificate' \| 'system' |
| `title` | VARCHAR(255) | NOT NULL | |
| `body` | TEXT | NULLABLE | |
| `is_read` | BOOLEAN | NOT NULL, DEFAULT false | |
| `link` | TEXT | NULLABLE | Frontend route to navigate to |
| `metadata` | JSONB | NULLABLE | |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Indexes:** `idx_notifications_user_id`, `idx_notifications_is_read`

---

### Table: `bookmarks`
**Why:** Allows users to bookmark specific lessons or topics for quick access.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `entity_type` | VARCHAR(20) | NOT NULL | 'lesson' \| 'topic' |
| `entity_id` | UUID | NOT NULL | lesson.id or topic.id |
| `note` | TEXT | NULLABLE | User annotation |
| `created_at` | TIMESTAMPTZ | NOT NULL | |

**Constraints:** `UNIQUE (user_id, entity_type, entity_id)`  
**Indexes:** `idx_bookmarks_user_course(user_id, course_id)`

---

### Table: `certificates`
**Why:** Issued when a user completes all lessons and passes the final quiz.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user_id` | UUID | FK → users.id ON DELETE CASCADE | |
| `course_id` | UUID | FK → courses.id ON DELETE CASCADE | |
| `issued_at` | TIMESTAMPTZ | NOT NULL | |
| `certificate_url` | TEXT | NOT NULL | Path to generated PDF certificate |
| `verification_code` | VARCHAR(64) | UNIQUE, NOT NULL | UUID-based public verification |

**Constraints:** `UNIQUE (user_id, course_id)`  
**Indexes:** `idx_certificates_user_id`, `idx_certificates_verification_code`

---

### Entity Relationship Summary

```
users ──< courses (owner_id)
users ──< course_enrollments >── courses
courses ──< lessons ──< topics ──< subtopics
courses ──< documents (1:1)
lessons ──< quizzes (1:1) ──< quiz_questions
users ──< quiz_attempts >── quizzes ──< quiz_attempt_answers
courses ──< flashcards >── flashcard_reviews (user)
users ──< chat_sessions >── courses ──< chat_messages
users ──< user_progress
users ──< analytics_events
users ──< notifications
users ──< bookmarks
users ──< certificates >── courses
```

---

# SECTION 4 — COMPLETE API DESIGN

**Base URL:** `http://localhost:8001/api/v1`  
**Auth:** Bearer JWT token in `Authorization: Bearer <token>` header  
**Versioning:** URL path versioning (`/api/v1/`) — version 2 can be added without breaking v1  
**Error Format:** `{"detail": "message", "code": "ERROR_CODE", "field": "field_name"}`

---

## 4.1 Auth Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login, receive JWT | No |
| POST | `/auth/refresh` | Refresh access token | Refresh token |
| POST | `/auth/logout` | Invalidate token | Yes |
| GET | `/auth/me` | Get current user profile | Yes |
| PUT | `/auth/me` | Update profile | Yes |
| POST | `/auth/change-password` | Change password | Yes |

**POST /auth/register**  
Request: `{email, password, full_name}`  
Response: `{id, email, full_name, created_at}`  
Errors: `422 VALIDATION_ERROR`, `409 EMAIL_EXISTS`

**POST /auth/login**  
Request: `{email, password}`  
Response: `{access_token, refresh_token, token_type, expires_in, user}`  
Errors: `401 INVALID_CREDENTIALS`

---

## 4.2 Course Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/courses` | List user's courses (paginated) | Yes |
| POST | `/courses/upload` | Upload PDF → trigger generation | Yes |
| GET | `/courses/{course_id}` | Get course detail + lessons | Yes |
| PUT | `/courses/{course_id}` | Update title/description | Yes |
| DELETE | `/courses/{course_id}` | Soft delete | Yes |
| GET | `/courses/{course_id}/status` | Poll generation status | Yes |
| POST | `/courses/{course_id}/enroll` | Enroll in course | Yes |
| GET | `/courses/{course_id}/structure` | Full lesson/topic tree | Yes |

**POST /courses/upload**  
Request: `multipart/form-data {file: PDF}`  
Response: `{course_id, status: "processing", estimated_time_sec}`  
Side effect: triggers Celery `generate_course_task`

**GET /courses/{course_id}/status**  
Response: `{status: "processing"|"ready"|"failed", progress_pct, current_step, error}`  
Used by frontend to poll and show progress bar.

---

## 4.3 Lesson Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/courses/{course_id}/lessons` | List lessons | Yes |
| GET | `/lessons/{lesson_id}` | Get lesson + topics + subtopics | Yes |
| PUT | `/lessons/{lesson_id}` | Edit lesson title/summary | Yes |
| GET | `/lessons/{lesson_id}/topics` | List topics | Yes |
| GET | `/topics/{topic_id}` | Get topic content | Yes |

---

## 4.4 Quiz Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/lessons/{lesson_id}/quiz` | Get quiz metadata | Yes |
| POST | `/quiz/{quiz_id}/attempt` | Start attempt, get questions | Yes |
| POST | `/quiz/attempts/{attempt_id}/submit` | Submit answers, get results | Yes |
| GET | `/quiz/attempts/{attempt_id}` | Get attempt details | Yes |
| GET | `/quiz/{quiz_id}/history` | User's attempt history | Yes |

**POST /quiz/{quiz_id}/attempt**  
Response: `{attempt_id, questions: [{id, text, type, options}], time_limit_min}`

**POST /quiz/attempts/{attempt_id}/submit**  
Request: `{answers: [{question_id, answer}]}`  
Response: `{score_pct, passed, results: [{question_id, is_correct, explanation, correct_answer}]}`

---

## 4.5 Chat Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/courses/{course_id}/chat/sessions` | List chat sessions | Yes |
| POST | `/courses/{course_id}/chat/sessions` | Create new session | Yes |
| GET | `/chat/sessions/{session_id}` | Get session + messages | Yes |
| POST | `/chat/sessions/{session_id}/messages` | Send message, get AI reply | Yes |
| DELETE | `/chat/sessions/{session_id}` | Delete session | Yes |

**POST /chat/sessions/{session_id}/messages**  
Request: `{content: "user question"}`  
Response: `{id, role: "assistant", content, sources, confidence, generation_time_ms}`

---

## 4.6 Progress Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/progress/courses` | Overall progress on all enrolled courses | Yes |
| GET | `/progress/courses/{course_id}` | Detailed progress for one course | Yes |
| POST | `/progress/event` | Record a progress event | Yes |

**POST /progress/event**  
Request: `{course_id, entity_type, entity_id, status, time_spent_sec}`

---

## 4.7 Search Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/search` | Global search across all courses | Yes |
| GET | `/search?course_id={id}` | Search within one course | Yes |

Query params: `q` (required), `course_id` (optional), `limit` (default 10), `type` (lessons\|topics\|chunks)

Response: `{lessons: [...], topics: [...], chunks: [{text, source, similarity}]}`

---

## 4.8 Flashcard Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/courses/{course_id}/flashcards` | All flashcards for course | Yes |
| GET | `/lessons/{lesson_id}/flashcards` | Flashcards for lesson | Yes |
| GET | `/flashcards/due` | Cards due for spaced review today | Yes |
| POST | `/flashcards/{card_id}/review` | Submit review rating | Yes |

**POST /flashcards/{card_id}/review**  
Request: `{rating: "again"|"hard"|"good"|"easy"}`  
Response: `{next_review_at, interval_days, ease_factor}`

---

## 4.9 Analytics Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/analytics/overview` | User dashboard stats | Yes |
| GET | `/analytics/courses/{course_id}` | Course-specific analytics | Yes |
| GET | `/analytics/activity` | Daily activity for heatmap | Yes |

---

## 4.10 Export Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| POST | `/export/courses/{course_id}/pdf` | Trigger PDF export | Yes |
| POST | `/export/courses/{course_id}/markdown` | Trigger Markdown export | Yes |
| GET | `/export/jobs/{job_id}` | Check export job status | Yes |
| GET | `/export/download/{job_id}` | Download exported file | Yes |

---

## 4.11 Notification Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/notifications` | Get all notifications | Yes |
| PUT | `/notifications/{id}/read` | Mark as read | Yes |
| PUT | `/notifications/read-all` | Mark all read | Yes |

---

## 4.12 Bookmark Endpoints

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/bookmarks` | All user bookmarks | Yes |
| POST | `/bookmarks` | Add bookmark | Yes |
| DELETE | `/bookmarks/{id}` | Remove bookmark | Yes |

---

# SECTION 5 — INSIGHTFORGE INTEGRATION

## Design Principle
CourseForge **never** calls InsightForge's internal classes directly from service files. All access goes through a single `InsightForgeEngine` adapter class. This means if InsightForge changes internally, only `engine.py` needs updating.

## Integration Architecture

```
CourseForge Services
       │
       ▼
backend/insightforge/engine.py   ← SINGLE INTEGRATION POINT
       │
       ├── IndexingPipeline (from InsightForge)
       │       ├── LoaderFactory (PDF, Text, Markdown)
       │       ├── CharacterChunker
       │       ├── EmbeddingService (all-MiniLM-L6-v2)
       │       ├── FAISSStore
       │       └── BM25Retriever
       │
       └── QueryPipeline (from InsightForge)
               ├── HybridRetriever
               ├── CrossEncoderReranker
               ├── ContextCompressor
               ├── ConfidenceEstimator
               ├── PromptBuilder (EXTENDED for CourseForge)
               └── GeminiGenerator (Groq llama-3.3-70b)
```

## `InsightForgeEngine` Interface

```python
# backend/insightforge/engine.py

class InsightForgeEngine:
    """
    Singleton adapter wrapping InsightForge-AI internals.
    CourseForge services ONLY interact through this class.
    """

    def index_document(self, file_path: str) -> IndexResult:
        """
        Ingest a PDF into FAISS + BM25.
        Returns: {doc_id, chunk_count, indexed}
        """

    def query(self, question: str, doc_ids: list[str] = None,
              prompt_override: str = None) -> QueryResult:
        """
        Run the full RAG pipeline.
        doc_ids: if provided, filter retrieved chunks to these documents only.
        prompt_override: use a custom prompt template instead of default.
        Returns: {answer, confidence, sources, chunks, generation_time_ms}
        """

    def retrieve_chunks(self, query: str, doc_ids: list[str] = None,
                        top_k: int = 10) -> list[ChunkResult]:
        """
        Retrieve raw chunks WITHOUT LLM generation.
        Used by: course_generator, quiz_generator, flashcard_generator.
        """

    def get_document(self, doc_id: str) -> dict | None:
        """Lookup document metadata in InsightForge registry."""

    def delete_document(self, doc_id: str) -> bool:
        """Remove document from FAISS + BM25 index."""
```

## Key Design Decisions

1. **`doc_ids` filter**: InsightForge's `HybridRetriever.retrieve()` doesn't natively scope to a subset of documents. The adapter adds a post-retrieval filter by `embedding.chunk.metadata["document_id"]`. This ensures a user's quiz question only references their own course's content.

2. **`prompt_override`**: CourseForge uses different prompt templates for each pipeline (course gen, quiz, chat, flashcard). The adapter accepts a fully-built prompt string, bypassing InsightForge's default `PromptBuilder`, and passes it directly to `GeminiGenerator.generate()`.

3. **`retrieve_chunks` without LLM**: Course generation, quiz generation, and flashcard generation need raw chunks — not LLM answers. This method gives direct chunk access without spending LLM tokens unnecessarily.

4. **No modifications to InsightForge**: Zero changes to InsightForge's source files. The adapter is 100% in CourseForge's codebase.

5. **Shared FAISS index with namespace tagging**: InsightForge uses a single global FAISS index. Documents are separated by their `document_id` in metadata. The adapter filters at query time. This avoids managing separate indexes per course.

---

# SECTION 6 — AI SYSTEM DESIGN

## 6.1 Prompt Manager

```
backend/prompts/
├── v1/
│   ├── course_structure.txt     # Extract structured outline
│   ├── lesson_content.txt       # Expand a topic into full lesson
│   ├── quiz_mcq.txt             # Generate MCQ questions
│   ├── quiz_tf.txt              # True/False questions
│   ├── quiz_open.txt            # Open-ended questions
│   ├── flashcard.txt            # Term/definition pairs
│   ├── chat_tutor.txt           # AI tutor system prompt
│   └── revision_summary.txt    # Compact review summary
└── prompt_manager.py
```

`PromptManager` loads prompts by name + version from disk. Future: versioned A/B testing.

**Never hardcode prompts in service files.** All prompts live in `prompts/v1/` and are loaded by `PromptManager`.

---

## 6.2 Course Generation Pipeline

```
Input: file_path (PDF)
─────────────────────────────────────────────────────────
Step 1: engine.index_document(file_path)
         └── Returns: doc_id, chunk_count

Step 2: engine.retrieve_chunks("main topics overview", doc_ids=[doc_id], top_k=20)
         └── Returns: raw chunks

Step 3: PromptManager.load("course_structure", "v1")
         └── Fill template with chunks
         └── engine.query(prompt) → JSON structure
         └── JSON Schema validation (jsonschema library)
         └── Retry up to 3x if JSON invalid

Step 4: For each lesson in structure:
         └── engine.retrieve_chunks(lesson.title, top_k=15)
         └── PromptManager.load("lesson_content", "v1")
         └── engine.query(prompt) → lesson text
         └── Save lessons + topics + subtopics to DB

Step 5: Store doc_id in documents.insightforge_doc_id
Step 6: Update course.status = "ready"
Step 7: Emit WebSocket event (or poll via /status)
Step 8: Create notification: "Your course is ready!"
─────────────────────────────────────────────────────────
Retry Strategy: exponential backoff (1s, 2s, 4s) for LLM calls
Error Handling: if generation fails, set course.status = "failed", store error message
Caching: Cache course structure in Redis for 1 hour (key: course:{id}:structure)
```

**Hallucination Prevention:**
- Prompt explicitly instructs: "Only use information from the provided context. Do not add external knowledge."
- All generated lesson content is traceable to `source_chunk_ids` stored in the DB.
- Confidence score < 0.4 triggers a warning flag on the lesson.

---

## 6.3 Quiz Generation Pipeline

```
Input: lesson_id
─────────────────────────────────────────────────────────
Step 1: Load lesson topics from DB
Step 2: For each topic:
         └── engine.retrieve_chunks(topic.title, top_k=5)
         └── PromptManager.load("quiz_mcq", "v1") → 3 MCQ
         └── PromptManager.load("quiz_tf", "v1") → 2 TF
Step 3: PromptManager.load("quiz_open", "v1") → 2 open for lesson
Step 4: JSON validation of each question
Step 5: Deduplication check (Jaccard similarity > 0.8 → discard)
Step 6: Save to quiz_questions table
─────────────────────────────────────────────────────────
```

---

## 6.4 Chat Pipeline

```
Input: session_id, user_message
─────────────────────────────────────────────────────────
Step 1: Load last 10 chat_messages from DB
Step 2: Build chat history string
Step 3: PromptManager.load("chat_tutor", "v1")
         └── Fill with: history, user_message
Step 4: engine.query(prompt, doc_ids=[course.doc_id])
         └── Returns: answer, sources, confidence, generation_time_ms
Step 5: Save user message to chat_messages
Step 6: Save assistant message with sources + confidence
Step 7: Return response to frontend
─────────────────────────────────────────────────────────
Rate Limiting: 60 messages/hour per user (Redis counter)
Caching: Do NOT cache chat responses (always fresh)
```

---

## 6.5 Flashcard Pipeline

```
Input: course_id
─────────────────────────────────────────────────────────
Step 1: Load all topics from DB
Step 2: For each topic:
         └── engine.retrieve_chunks(topic.title, top_k=3)
         └── PromptManager.load("flashcard", "v1")
         └── engine.query(prompt) → [{front, back}]
         └── JSON validation
         └── Save to flashcards table
Step 3: Initialize flashcard_reviews with default SM-2 values
─────────────────────────────────────────────────────────
```

---

## 6.6 Revision Pipeline

```
Input: course_id
─────────────────────────────────────────────────────────
Step 1: Load all lessons from DB
Step 2: For each lesson:
         └── engine.retrieve_chunks(lesson.title, top_k=10)
         └── PromptManager.load("revision_summary", "v1")
         └── engine.query(prompt) → compact summary
Step 3: Combine summaries into structured revision document
Step 4: Return as structured JSON (renderable in UI)
─────────────────────────────────────────────────────────
Caching: Cache revision per course in Redis (TTL 24h, key: revision:{course_id})
```

---

## 6.7 Search Pipeline

```
Input: query, course_id (optional)
─────────────────────────────────────────────────────────
Step 1: engine.retrieve_chunks(query, doc_ids=[...], top_k=10)
         └── If course_id: filter to that course's doc_id
         └── Else: search across all user's courses
Step 2: PostgreSQL ILIKE search on lessons.title, topics.title
Step 3: Merge + rank: hybrid score + title match boost
Step 4: Return: {lessons, topics, chunks}
─────────────────────────────────────────────────────────
```

---

## 6.8 Analytics Pipeline

```
Input: user_id, time_range
─────────────────────────────────────────────────────────
Step 1: Query analytics_events aggregated by event_type, date
Step 2: Query user_progress for completion rates
Step 3: Query quiz_attempts for average scores
Step 4: Build response:
         {total_study_time, courses_in_progress, courses_completed,
          quiz_avg_score, flashcards_reviewed, daily_activity[]}
─────────────────────────────────────────────────────────
Caching: Cache analytics in Redis (TTL 5 minutes)
```

---

## 6.9 Background Job System (Celery + Redis)

```python
# Task definitions
generate_course_task(course_id: str, file_path: str)
    └── Calls: CourseGenerationPipeline.run()

generate_quiz_task(lesson_id: str)
    └── Calls: QuizGenerationPipeline.run()

export_task(course_id: str, format: str)
    └── Calls: ExportService.export()
```

- Celery broker: Redis
- Task result backend: Redis
- Task timeout: 10 minutes for generation
- Retry on failure: 3 attempts with exponential backoff
- Failed tasks: write error to `courses.generation_error`

---

## 6.10 JSON Output Validation

All LLM responses that produce structured data (course structure, questions, flashcards) are validated against JSON schemas before saving. Invalid responses trigger a retry (max 3). After 3 failures, the task is marked failed with a descriptive error.

---

# SECTION 7 — UI/UX DESIGN SYSTEM

## 7.1 Design Inspiration & Philosophy
**Inspired by:** Linear (clean, functional), Notion (content-first), Vercel (dark + precise), Perplexity (citation-aware), ChatGPT (chat interface), Stripe (typography + trust)

**Philosophy:** Dark-mode-first, minimal friction, every interaction feels instant. Content is the hero.

---

## 7.2 Color Palette

```css
:root {
  /* Background layers */
  --bg-base:      #0a0a0f;    /* Deepest background */
  --bg-surface:   #111118;    /* Cards, panels */
  --bg-elevated:  #1a1a24;    /* Modals, dropdowns */
  --bg-highlight: #22223a;    /* Hover states */

  /* Brand */
  --brand-500:    #7c6ff7;    /* Primary purple (Perplexity-inspired) */
  --brand-400:    #9d97f9;    /* Lighter brand */
  --brand-600:    #5a54d4;    /* Darker brand */
  --brand-glow:   rgba(124, 111, 247, 0.15);

  /* Text */
  --text-primary:   #f0f0f5;
  --text-secondary: #9898b0;
  --text-muted:     #55556a;
  --text-inverse:   #0a0a0f;

  /* Status */
  --success:  #22d39a;
  --warning:  #f5a623;
  --error:    #ff4d6a;
  --info:     #3db0f7;

  /* Borders */
  --border-subtle:  rgba(255,255,255,0.06);
  --border-default: rgba(255,255,255,0.10);
  --border-strong:  rgba(255,255,255,0.20);

  /* Gradients */
  --gradient-brand: linear-gradient(135deg, #7c6ff7 0%, #5a54d4 100%);
  --gradient-glow:  radial-gradient(ellipse at center, rgba(124,111,247,0.2), transparent 70%);
}
```

---

## 7.3 Typography

**Font Stack:**
- Headings: `Inter` (Google Fonts) — weight 700/600
- Body: `Inter` — weight 400/500
- Code: `JetBrains Mono` — monospace for lesson code blocks

```css
--font-display: 'Inter', system-ui, sans-serif;
--font-mono:    'JetBrains Mono', monospace;

--text-xs:   0.75rem;   /* 12px */
--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.25rem;   /* 20px */
--text-2xl:  1.5rem;    /* 24px */
--text-3xl:  1.875rem;  /* 30px */
--text-4xl:  2.25rem;   /* 36px */
```

---

## 7.4 Spacing & Grid

```css
--space-1:  0.25rem;  /* 4px */
--space-2:  0.5rem;   /* 8px */
--space-3:  0.75rem;  /* 12px */
--space-4:  1rem;     /* 16px */
--space-6:  1.5rem;   /* 24px */
--space-8:  2rem;     /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

**Grid:** 12-column CSS Grid. Sidebar = 240px fixed. Main content = fluid. Max content width = 1280px.

**Border Radius:**
```css
--radius-sm: 6px;
--radius-md: 10px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-full: 9999px;
```

---

## 7.5 Component Design Language

**Cards:** Glassmorphism on dark — `background: var(--bg-surface)`, `border: 1px solid var(--border-subtle)`, `border-radius: var(--radius-lg)`, subtle `box-shadow: 0 0 0 1px rgba(255,255,255,0.04)`

**Buttons:**
- Primary: Brand gradient, white text, hover scale(1.02) + glow
- Secondary: Surface bg, border, brand text
- Danger: error color
- Ghost: transparent, hover highlight

**Input Fields:** Dark bg, border on focus changes to brand color, smooth transition

**Sidebar:** 240px fixed, bg-surface, icons + labels, active state with brand-left-border + bg-highlight

**Progress Bar:** Animated fill, brand gradient, rounded

**Modals:** Center slide-up animation, backdrop blur, elevated surface

**Toasts:** Top-right, slide-in from right, auto-dismiss 4s

**Loading States:** Skeleton screens (not spinners) for content areas. Spinner only for action buttons.

**Empty States:** Illustration + headline + CTA button. Never just a blank space.

**Animations:**
```css
--transition-fast:   150ms ease;
--transition-normal: 250ms ease;
--transition-slow:   400ms ease;
/* Page transitions: fade-in 200ms */
/* Card hover: translateY(-2px) + shadow grow */
/* Button click: scale(0.97) */
/* Sidebar collapse: slide 250ms */
```

---

## 7.6 Dark Mode

Dark mode is the **default and only mode** for MVP. Light mode is a future phase extension. Design tokens are all defined in `:root` (dark). Light mode would swap values via `[data-theme="light"]`.

---

## 7.7 Mobile Layout

- Sidebar collapses to bottom navigation bar on mobile (< 768px)
- Cards become full-width stacked
- Chat window becomes full-screen overlay
- Quiz remains single-question-per-screen
- Flashcard flip works with swipe gesture (via touch events)

---

## 7.8 Accessibility

- All interactive elements have `aria-label`
- Keyboard navigable: Tab + Enter + Escape for modals
- Color contrast ratio ≥ 4.5:1 for all text
- Focus ring visible on all focusable elements
- Alt text on all images
- Reduced motion support: `prefers-reduced-motion` media query respected

---

# SECTION 8 — SCREEN INVENTORY

| # | Screen | Route | Purpose | Key Components | APIs | DB Tables |
|---|---|---|---|---|---|---|
| 1 | Login | `/login` | User auth | AuthLayout, Input, Button | POST /auth/login | users |
| 2 | Register | `/register` | New account | AuthLayout, Input, Button | POST /auth/register | users |
| 3 | Dashboard | `/dashboard` | Home overview | AppLayout, CourseCard, ProgressChart, ActivityHeatmap | GET /courses, GET /analytics/overview | courses, enrollments, analytics |
| 4 | All Courses | `/courses` | Browse all courses | AppLayout, CourseGrid, SearchBar | GET /courses | courses |
| 5 | Create Course | `/courses/new` | Upload PDF | AppLayout, UploadZone, UploadProgress | POST /courses/upload | courses, documents |
| 6 | Course Detail | `/courses/:id` | Course landing page | AppLayout, LessonList, CourseProgress, Tabs | GET /courses/:id, GET /progress/courses/:id | courses, lessons, enrollments |
| 7 | Learn (Lesson) | `/courses/:id/learn/:lessonId` | Read lesson content | AppLayout, TopicTree, LessonViewer, ChatWindow, Bookmark | GET /lessons/:id, POST /progress/event | lessons, topics, progress |
| 8 | Quiz | `/courses/:id/quiz/:quizId` | Take quiz | AppLayout, QuizQuestion, QuizTimer | POST /quiz/:id/attempt | quizzes, questions, attempts |
| 9 | Quiz Result | `/quiz/attempts/:id` | View results | AppLayout, QuizResult | GET /quiz/attempts/:id | attempts, answers |
| 10 | Chat | `/courses/:id/chat` | AI Tutor chat | AppLayout, ChatWindow, ChatInput, SourceCitation | GET + POST /chat/sessions | chat_sessions, messages |
| 11 | Flashcards | `/courses/:id/flashcards` | Study flashcards | AppLayout, FlashcardDeck, FlashcardFlip | GET /courses/:id/flashcards, POST /flashcards/:id/review | flashcards, reviews |
| 12 | Search | `/search` | Global search | AppLayout, SearchBar, SearchResults | GET /search | lessons, topics (+ chunks) |
| 13 | Analytics | `/analytics` | Learning stats | AppLayout, ProgressChart, ActivityHeatmap, StatCards | GET /analytics/overview, /activity | analytics_events, progress |
| 14 | Revision | `/courses/:id/revision` | Compact review | AppLayout, LessonViewer (read-only) | GET /courses/:id/revision | lessons, topics |
| 15 | Export | `/courses/:id/export` | Download course | AppLayout, Button | POST /export/courses/:id/pdf | courses |
| 16 | Bookmarks | `/bookmarks` | Saved items | AppLayout, LessonList | GET /bookmarks | bookmarks |
| 17 | Notifications | `/notifications` | All alerts | AppLayout, NotificationList | GET /notifications | notifications |
| 18 | Settings | `/settings` | Account settings | AppLayout, Input, Button | PUT /auth/me | users |
| 19 | Not Found | `*` | 404 page | EmptyState, Button | — | — |

**Mobile Layout Notes:**  
- Dashboard: stacked cards, bottom nav
- Learn: topic tree becomes collapsible side panel
- Chat: full-screen
- Quiz: single question per screen, swipe between

---

# SECTION 9 — COMPONENT INVENTORY

## Atomic UI Components (`/components/ui/`)

| Component | Props | Used By | Future Reuse |
|---|---|---|---|
| `Button` | variant, size, loading, disabled, onClick | Every page | Always |
| `Input` | label, error, type, value, onChange | Auth, Settings | Always |
| `Badge` | variant (status/difficulty/type), label | CourseCard, QuizQuestion | Always |
| `Card` | children, hover, className | CourseCard, QuizCard, etc. | Always |
| `Modal` | isOpen, onClose, title, children | Delete confirm, Export | Always |
| `Tooltip` | content, children | Sidebar icons, difficulty badge | Always |
| `Spinner` | size | Button loading states | Always |
| `Progress` | value, max, label | CourseProgress, UploadProgress | Always |
| `Tabs` | tabs, activeTab, onChange | CourseDetail (Lessons/Quiz/Flashcards) | Always |
| `Avatar` | src, name, size | Topbar, Sidebar | Always |
| `Dropdown` | trigger, items | Topbar, CourseCard actions | Always |
| `Toast` | type, message, duration | Global (via uiStore) | Always |
| `EmptyState` | illustration, title, description, action | All empty list states | Always |

## Layout Components (`/components/layout/`)

| Component | Used By | Notes |
|---|---|---|
| `AppLayout` | All authenticated pages | Sidebar + Topbar + main content |
| `Sidebar` | AppLayout | Nav links, course list |
| `Topbar` | AppLayout | Search, notifications, avatar |
| `AuthLayout` | Login, Register | Centered card layout |

## Feature Components

| Component | Used By | Future Reuse |
|---|---|---|
| `CourseCard` | CoursesPage, Dashboard | Course list views |
| `CourseGrid` | CoursesPage | Grid layout for cards |
| `LessonList` | CourseDetail, Bookmarks | Vertical lesson list |
| `LessonViewer` | LearnPage, RevisionPage | Markdown content renderer |
| `TopicTree` | LearnPage | Collapsible topic navigator |
| `CourseProgress` | CourseDetail, Dashboard | Circular progress + stats |
| `ChatWindow` | ChatPage, LearnPage (side panel) | Reused in two contexts |
| `ChatMessage` | ChatWindow | User/assistant message bubble |
| `ChatInput` | ChatWindow | Text + send button |
| `SourceCitation` | ChatMessage | Clickable source chips |
| `QuizCard` | QuizPage list | Quiz summary card |
| `QuizQuestion` | QuizPage | Renders MCQ/TF/Open question |
| `QuizResult` | QuizResultPage | Score + per-question review |
| `QuizTimer` | QuizPage | Countdown if time_limit set |
| `FlashcardDeck` | FlashcardsPage | Card stack navigator |
| `FlashcardFlip` | FlashcardDeck | 3D flip animation |
| `SearchBar` | Topbar (global), SearchPage | Debounced input |
| `SearchResults` | SearchPage | Categorized results |
| `ProgressChart` | Analytics, Dashboard | Line chart (recharts) |
| `ActivityHeatmap` | Analytics | GitHub-style heatmap |
| `UploadZone` | CreateCoursePage | Drag-and-drop PDF |
| `UploadProgress` | CreateCoursePage | Step-by-step generation progress |

---

# SECTION 10 — STATE MANAGEMENT

## Technology: **Zustand** (lightweight, no boilerplate)

React Query (TanStack Query) for **server state** (API calls, caching, invalidation).  
Zustand for **global UI state** (auth, sidebar, theme).

---

## 10.1 authStore (Zustand)

```javascript
{
  user: null | UserObject,
  accessToken: null | string,
  isAuthenticated: boolean,
  isLoading: boolean,

  // Actions
  login(credentials) → set token + user,
  logout() → clear all state,
  refreshToken() → get new access token,
  updateUser(partial) → update user fields
}
```
Token stored in `localStorage`. Axios interceptor attaches token to every request. Interceptor detects 401 → tries refresh → if fails → logout.

---

## 10.2 courseStore (Zustand)

```javascript
{
  courses: [],             // Cached course list
  currentCourse: null,     // Detailed view
  generationStatus: {}     // {courseId: {status, progress_pct, step}}
}
```
Most course data fetched via React Query (`useCourse(courseId)` hook). Store holds polling state for generation.

---

## 10.3 chatStore (Zustand)

```javascript
{
  sessions: {},            // {courseId: SessionObject}
  activeSessionId: null,
  messages: {},            // {sessionId: Message[]}
  isTyping: false,         // AI is generating
  streamBuffer: ""         // Future: streaming support
}
```

---

## 10.4 progressStore (Zustand)

```javascript
{
  courseProgress: {}       // {courseId: {pct, completedLessons, totalLessons}}
}
```
Updated optimistically on `POST /progress/event`.

---

## 10.5 quizStore (Zustand)

```javascript
{
  activeAttempt: null,     // {attempt_id, questions, answers, timeLeft}
  answers: {},             // {question_id: answer}
  isSubmitting: false
}
```
Local state — cleared on quiz exit.

---

## 10.6 searchStore (Zustand)

```javascript
{
  query: "",
  results: null,
  isSearching: false,
  recentSearches: []
}
```

---

## 10.7 uiStore (Zustand)

```javascript
{
  sidebarCollapsed: false,
  activeModal: null,       // modal name or null
  toasts: [],
  theme: "dark"
}
```

---

## 10.8 React Query Usage

- `useQuery(['courses'], fetchCourses)` — auto-cached, refetches on focus
- `useQuery(['course', id], fetchCourse)` — course detail
- `useMutation(uploadCourse)` — POST upload, invalidate courses list on success
- `useQuery(['progress', courseId], fetchProgress)` — auto-refreshed
- `useInfiniteQuery(['search', query], fetchSearch)` — paginated search results

**Caching strategy:** staleTime = 60s for most data. Cache invalidated on mutations.

**Optimistic Updates:** When user marks a lesson complete, `progressStore` is updated immediately before the API call resolves.

---

# SECTION 11 — DEVELOPMENT ROADMAP

## Phase 0 — Foundation (Week 1-2)
**Objective:** Infrastructure, tooling, empty shells working end-to-end.

**Deliverables:**
- PostgreSQL + Redis running via Docker Compose
- FastAPI app skeleton with health endpoint
- Alembic migrations for all tables
- React + Vite frontend running
- Zustand stores initialized
- Axios client + auth interceptors
- JWT auth (`/auth/register`, `/auth/login`, `/auth/me`)
- Login + Register pages (no styling yet)
- `InsightForgeEngine` adapter class (wiring to existing InsightForge)

**Future Compatibility Check:** All DB migrations must produce final schema. No additive migrations required in Phase 1.

**Testing Checklist:**
- [ ] DB tables created correctly
- [ ] Register + Login returns valid JWT
- [ ] InsightForgeEngine.index_document() works
- [ ] InsightForgeEngine.query() works

**Git Commit:** `feat: foundation — auth, db, insightforge adapter`

---

## Phase 1 — Upload & Course Generation (Week 3-4)
**Objective:** User can upload a PDF and get a generated course.

**Deliverables:**
- POST /courses/upload endpoint + Celery task
- `CourseGenerationPipeline` (index → structure → lessons → topics)
- `PromptManager` with v1 prompts
- `QuizGenerationPipeline` (per lesson)
- `FlashcardGenerationPipeline`
- DB: courses, documents, lessons, topics, subtopics, quizzes, questions, flashcards populated
- Frontend: CreateCoursePage (UploadZone + UploadProgress)
- Frontend: Polling GET /courses/:id/status
- Notifications on completion

**Future Compatibility Check:** All AI outputs save `source_chunk_ids`. All prompts versioned in /prompts/v1/. No hardcoded prompts.

**Testing Checklist:**
- [ ] Upload a real PDF → course generated in DB
- [ ] Course structure JSON validated
- [ ] Quiz questions saved
- [ ] Flashcards saved
- [ ] Status polling works

**Git Commit:** `feat: pdf upload + async course generation pipeline`

---

## Phase 2 — Learning Experience (Week 5-6)
**Objective:** User can read their course, track progress, take quizzes, chat.

**Deliverables:**
- Frontend: Dashboard, CoursesPage, CourseDetailPage
- Frontend: LearnPage (lesson viewer + topic tree)
- Frontend: ChatPage + ChatWindow
- Frontend: QuizPage + QuizResultPage
- Frontend: FlashcardsPage
- Backend: All lesson, quiz, chat, progress, flashcard endpoints
- Progress tracking + events
- Bookmark system

**Future Compatibility Check:** ChatWindow designed to accept `doc_ids` — future multi-doc chat requires no rewrite. Quiz system supports multiple question types already in schema.

**Git Commit:** `feat: learning experience — lessons, quiz, chat, flashcards, progress`

---

## Phase 3 — Search, Analytics, Export (Week 7-8)
**Objective:** Power user features — find anything, understand progress, export content.

**Deliverables:**
- Frontend: SearchPage + SearchBar in Topbar
- Frontend: AnalyticsPage (charts + heatmap)
- Backend: Search endpoint (hybrid InsightForge + DB)
- Backend: Analytics aggregation endpoints
- Backend: Export to PDF + Markdown (Celery task)
- Frontend: RevisionPage

**Git Commit:** `feat: search, analytics, export, revision`

---

## Phase 4 — Polish, Performance, Deploy (Week 9-10)
**Objective:** Production-ready.

**Deliverables:**
- Full CSS design system applied to all screens
- Animations + transitions
- Mobile responsive layout
- Accessibility pass
- Error boundaries on all routes
- Docker Compose production config
- Nginx reverse proxy
- Environment variable documentation
- README with setup instructions
- Full test suite

**Git Commit:** `feat: production polish + deployment`

---

## Future Phases (Not in MVP)
- Phase 5: Multi-user collaboration, shared courses
- Phase 6: Public course marketplace
- Phase 7: Light mode
- Phase 8: Streaming LLM responses (SSE)
- Phase 9: Voice mode (TTS/STT)
- Phase 10: Mobile app (React Native)

---

# SECTION 12 — PROJECT DECISION LOG

## Architecture Decisions

| Decision | Choice | Rationale | Never Change |
|---|---|---|---|
| Backend framework | FastAPI | Async, type-safe, fast, Pydantic native | Yes |
| Frontend framework | React 18 + Vite | Fast builds, large ecosystem | Yes |
| State management | Zustand + React Query | Minimal boilerplate, server state separation | Yes |
| Primary database | PostgreSQL | ACID, JSONB, arrays, UUID, full-text | Yes |
| Cache + jobs broker | Redis | Multi-purpose: sessions, Celery, cache | Yes |
| Background jobs | Celery | Python-native, reliable, battle-tested | Yes |
| CSS approach | Vanilla CSS with custom properties | No runtime overhead, full control | Yes |
| API versioning | URL path `/api/v1/` | Non-breaking version addition | Yes |
| UUID primary keys | All tables | Distributed-safe, no sequential leak | Yes |
| Soft deletes | `deleted_at` on users + courses | Data recovery, audit trail | Yes |
| Auth mechanism | JWT (access + refresh) | Stateless, standard | Yes |

## Database Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Progress tracking | Event-log pattern (user_progress) | Queryable history, no data loss |
| Analytics | Append-only table | Never update, partition monthly at scale |
| Flashcard algorithm | SM-2 spaced repetition | Industry standard, proven effective |
| JSONB for flexible data | options, sources, metadata columns | Avoids EAV tables, queryable |
| Array columns (tags, chunk_ids) | PostgreSQL TEXT[] | Efficient for small arrays |

## Prompt Decisions

| Decision | Rationale |
|---|---|
| All prompts in files, not code | Easy to edit without code change |
| Versioned (v1/) | Safe A/B testing in future |
| JSON output schema validation | Prevent broken AI outputs from corrupting DB |
| Max 3 retries on LLM failure | Balance cost vs reliability |
| Hallucination guard in every prompt | Instruction to use ONLY context |

## InsightForge Decisions

| Decision | Rationale |
|---|---|
| Zero modifications to InsightForge | Preserve stability of existing system |
| Single adapter class (engine.py) | One file to update if InsightForge changes |
| doc_ids filter at query time | Namespace isolation without separate indexes |
| retrieve_chunks without LLM | Avoid unnecessary token spend on generation tasks |

## Things Never To Change
- Database primary key type (UUID)
- API base path (`/api/v1/`)
- Auth token mechanism (JWT)
- InsightForge adapter interface signatures
- Prompt file locations and naming convention
- Folder structure as defined in Section 2

## Things That Can Be Extended
- Add new event types to `analytics_events.event_type`
- Add new prompt versions (v2/, v3/)
- Add new API endpoints without breaking existing ones
- Add new question types to `quiz_questions.question_type`
- Add columns to any table via Alembic migration (never remove/rename)

---

# SECTION 13 — RISK ANALYSIS

## Technical Risks

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| LLM produces invalid JSON for course structure | High | Medium | JSON schema validation + retry (max 3) + fallback to raw text storage |
| InsightForge FAISS index grows large (>1M chunks) | High | Low (MVP) | Partition FAISS indexes per user in Phase 5 |
| Celery task queue backup (many uploads at once) | Medium | Medium | Celery auto-scaling workers, task priority queue |
| PostgreSQL connection pool exhaustion | Medium | Low | `asyncpg` pool size config, connection limits |
| File storage disk full | Medium | Low | File size limits on upload (50MB), periodic cleanup |

## Performance Risks

| Risk | Mitigation |
|---|---|
| Course generation takes > 5 minutes | Break into smaller Celery sub-tasks, show step-by-step progress |
| Search returns too many results | Limit to top 10, paginate |
| Analytics queries slow on large datasets | Aggregate nightly into summary tables (Phase 3+) |
| Chat latency > 3s | Redis cache for repeated questions per session |

## AI Risks

| Risk | Mitigation |
|---|---|
| Hallucination in course content | Prompt guardrails + source_chunk_ids traceability |
| Quiz questions too hard/easy | Prompt specifies difficulty distribution |
| Repetitive flashcards | Jaccard deduplication before save |
| LLM API rate limit (Groq) | Exponential backoff, respect `Retry-After` header |
| LLM API key exposed | `.env` file, never commit to git |

## Database Risks

| Risk | Mitigation |
|---|---|
| Schema change needed mid-project | Design is complete — Alembic adds, never removes |
| Foreign key cascade deletes wrong data | Verify cascade behavior in tests before launch |
| analytics_events table too large | Monthly partitioning by `created_at` from day one |

## Deployment Risks

| Risk | Mitigation |
|---|---|
| Environment variable misconfiguration | `.env.example` with all required vars documented |
| Docker container memory limit | Set resource limits in docker-compose, monitor |
| CORS blocking frontend requests | Explicit CORS config in FastAPI middleware |

---

# SECTION 14 — TESTING STRATEGY

## Backend Tests (`/tests/backend/`)

### Unit Tests
- `test_course_generator.py` — mock InsightForge engine, assert DB writes
- `test_quiz_generator.py` — mock LLM responses, assert question schema
- `test_chat_service.py` — mock retrieval, assert source citation format
- `test_prompt_manager.py` — assert prompt loading, templating
- `test_json_validator.py` — valid + invalid JSON scenarios

### Integration Tests
- `test_upload_flow.py` — upload real PDF → verify course created in DB
- `test_course_generation.py` — full pipeline end-to-end with test PDF
- `test_auth.py` — register → login → refresh → protected endpoint
- `test_quiz_attempt.py` — start attempt → submit → check scoring
- `test_search.py` — query returns expected lesson + chunk results

### Tools: `pytest`, `httpx` (async test client), `factory_boy` (test data), `pytest-asyncio`

---

## Frontend Tests (`/tests/frontend/`)

- Component tests with **Vitest + React Testing Library**
- `ChatWindow.test.jsx` — renders messages, submit triggers API
- `QuizQuestion.test.jsx` — MCQ/TF/Open renders correctly
- `FlashcardFlip.test.jsx` — flip animation state toggle
- `UploadZone.test.jsx` — drag event, file validation

---

## AI Tests

- **Prompt regression tests**: Feed known PDF → assert course structure contains expected keys
- **Output schema tests**: Assert every LLM response passes JSON schema validation
- **Hallucination smoke test**: Ask question about content NOT in PDF → expect low confidence or refusal

---

## Database Tests

- **Migration tests**: Run all Alembic migrations on clean DB, verify schema
- **Constraint tests**: Verify unique constraints (email, enrollment, certificate)
- **Cascade tests**: Delete course → verify lessons, topics, quizzes, flashcards deleted

---

## Edge Cases

| Scenario | Expected Behavior |
|---|---|
| Upload corrupt/empty PDF | 400 error with clear message |
| LLM fails all 3 retries | Course status = "failed", error saved |
| Quiz attempt > max_attempts | 403 error "Max attempts reached" |
| Search with empty query | Return empty results, not error |
| Flashcard review for non-existent card | 404 error |
| Concurrent uploads from same user | Both succeed, separate courses |
| Chat message with SQL injection | Pydantic validation sanitizes input |

---

## Deployment Verification

- [ ] `GET /health` returns 200
- [ ] `POST /auth/register` creates user in DB
- [ ] Upload PDF → Celery processes → course appears in `/courses`
- [ ] Chat returns response with sources
- [ ] Export generates downloadable file

---

# SECTION 15 — FINAL ARCHITECTURE REVIEW

## Self-Critique (Principal Engineer Review)

### ✅ What is Solid

1. **InsightForge integration is clean.** Single adapter class. Zero modifications to InsightForge.
2. **Database schema is complete.** Every feature has its tables. Foreign keys are correct. Indexes cover all query patterns.
3. **API versioning is correct.** `/api/v1/` prefix allows future v2 without breaking clients.
4. **Background jobs are isolated.** Generation never blocks the HTTP request.
5. **Prompt system is versioned.** Changing prompts never requires code changes.
6. **State management is appropriate.** Zustand for UI, React Query for server — no overlap.
7. **UUID primary keys throughout.** Future-safe.
8. **Soft deletes on critical entities.** Data recovery is possible.

### ⚠️ Potential Issues Identified & Resolved

| Issue | Resolution Applied |
|---|---|
| InsightForge's FAISS is a single global index — could mix users' data | `doc_ids` filter in adapter at query time ensures isolation |
| Course generation could time out for large PDFs | Break into sub-tasks, set 10-min timeout, show progress steps |
| No streaming for chat | Noted as Phase 5+ extension. Architecture ready (streamBuffer in chatStore) |
| Quiz open-ended grading requires LLM | `quiz_questions.correct_answer` stores model answer; grading uses LLM comparison prompt. Field is already in schema |
| analytics_events could become enormous | Noted monthly partition — implement from day one in Alembic |
| Spaced repetition state (SM-2) stored per review, not aggregated | `flashcard_reviews` table stores full review history. Latest state computed from most recent row per user+card |

### ❌ Things NOT Missing

Going through the checklist:
- Auth ✅ | Dashboard ✅ | Courses ✅ | Lessons ✅ | Topics ✅ | Subtopics ✅
- Progress ✅ | Quiz ✅ | Attempts ✅ | Flashcards ✅ | Spaced repetition ✅
- Chat ✅ | AI Tutor prompt ✅ | Sources + citations ✅ | Confidence ✅
- Search ✅ | Analytics ✅ | Export ✅ | Revision ✅ | Bookmarks ✅
- Notifications ✅ | Certificates ✅ | Background jobs ✅
- Hallucination prevention ✅ | JSON validation ✅ | Retry strategy ✅
- Prompt versioning ✅ | Rate limiting ✅ | Caching strategy ✅
- Mobile layout ✅ | Accessibility ✅ | Dark mode ✅
- Testing strategy ✅ | Risk analysis ✅ | Decision log ✅

### Final Verdict

> **This architecture is approved for implementation.**  
> No major rewrites are anticipated. The schema handles all current and future features as described.  
> The InsightForge integration is designed for zero-modification stability.  
> Begin with Phase 0 and proceed sequentially through Phase 4.

---

*End of CourseForge AI Software Design Package v1.0*
