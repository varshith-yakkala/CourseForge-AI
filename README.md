# CourseForge AI — AI-Powered Interactive Learning Platform (v1.0.0)

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.x-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)
![Celery](https://img.shields.io/badge/Celery-5.4+-37814A.svg)
![Tests](https://img.shields.io/badge/tests-36%2F36%20passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**CourseForge AI** is a state-of-the-art AI-powered learning platform and personal **AI Learning Coach** that transforms raw PDF documents into structured, interactive courses. Powered by a custom **Retrieval-Augmented Generation (RAG)** adapter, CourseForge AI parses document context, synthesizes course blueprints, generates interactive Markdown lessons with code syntax highlighting, delivers SuperMemo SM-2 spaced repetition flashcards, adaptive quizzes, habit heatmaps, and proactive AI coaching advice.

---

## 🚀 One-Command Docker Quickstart

Launch the entire production stack (PostgreSQL, Redis, Celery Worker, FastAPI Backend, React Frontend, and Nginx Reverse Proxy) in a single command:

```bash
# Clone repository
git clone https://github.com/varshith-yakkala/CourseForge-AI.git
cd CourseForge-AI

# Launch production stack
docker-compose up -d --build
```

Access the application at `http://localhost`.

---

## 🌟 Key Platform Features

- **📄 Smart PDF Document Ingestion**: Upload any PDF document with instant MIME validation, page extraction, and chunking.
- **🔍 Hybrid Retrieval Engine**: Custom InsightForge-AI adapter utilizing FAISS vector search and BM25 keyword matching.
- **🏗️ Automated Course Blueprint Generator**: Synthesizes structured course syllabi (Lessons, Topics, Subtopics, Key Terms) powered by Groq LLM.
- **⚡ On-Demand Lesson Generation**: Lessons are generated lazily when opened, minimizing unnecessary LLM token consumption.
- **🎯 Adaptive Quizzes & Pool Sampling**: Multiple choice, True/False, fill-in-the-blank, short answer, and code output questions with difficulty selection (Beginner, Intermediate, Advanced) and partial credit scoring.
- **🃏 SuperMemo SM-2 Flashcards**: 3D flip-card reader with confidence self-assessments recalculating spaced repetition intervals.
- **🤖 Proactive AI Learning Coach**: Floating AI Coach widget providing contextual next-step guidance and streak reminders.
- **📅 Adaptive Study Planner & Timeline**: Dynamic daily schedule rebalancing, pace predictions (completion date & on-time probability %), and multi-event visual calendar.
- **📈 AI Weekly Intelligence Reports**: Synthesizes learning trends, weak/strong topic breakdowns, and exportable Markdown progress reports.
- **🔒 Production Hardening**: Multi-stage Dockerfiles, Nginx proxy, security headers (`X-Frame-Options`, `HSTS`, `CSP`), `X-Request-ID` tracing, and health monitoring endpoints (`/health`, `/ready`, `/metrics`).
- **🧪 100% Test Coverage**: Verified with 23 Pytest backend tests and 13 Vitest frontend component tests (36/36 passing).


---

## 📸 Screenshots Showcase

*(Screenshots can be captured during demonstration)*

| Screen | Description | Placeholder |
|--------|-------------|-------------|
| **Landing Page** | Dark glassmorphism hero section with interactive CTA | `![Landing Page](docs/screenshots/landing.png)` |
| **Dashboard** | Course cards grid with status badges & empty state | `![Dashboard](docs/screenshots/dashboard.png)` |
| **Course Detail** | Nested course blueprint accordion & search interface | `![Course Detail](docs/screenshots/course_detail.png)` |
| **Lesson Viewer** | Interactive lesson reader with Table of Contents & Markdown | `![Lesson Viewer](docs/screenshots/lesson_viewer.png)` |
| **AI Lesson Tutor** | Slide-over AI assistant panel answering lesson questions | `![AI Tutor](docs/screenshots/ai_tutor.png)` |
| **Syntax Highlighting**| GFM code blocks highlighted in GitHub Dark theme | `![Syntax Highlighting](docs/screenshots/syntax_highlighting.png)` |

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User([User / Web Browser]) -->|HTTP / REST| Frontend[React 18 + Vite Frontend]
    Frontend -->|Axios / React Query| FastAPI[FastAPI Backend Server]
    
    FastAPI -->|JWT Security| Auth[Auth Service]
    FastAPI -->|Async Session| DB[(PostgreSQL Database)]
    FastAPI -->|Task Dispatch| Redis[(Redis Broker)]
    
    Redis -->|Background Processing| Celery[Celery Task Worker]
    Celery -->|Index / Retrieve| RAG[InsightForge RAG Adapter]
    
    FastAPI -->|RAG Context + Prompt| RAG
    RAG -->|FAISS + BM25 Hybrid Search| Storage[(PDF Document Chunks)]
    RAG -->|Generate Content| LLM[Groq LLM API]
    
    LLM -->|Structured Markdown| LessonCache[(Lesson DB Cache)]
    LessonCache -->|Cached Lesson| Frontend
    Frontend -->|Scoped Q&A| TutorPanel[AI Lesson Tutor Panel]
```

### End-to-End Workflow
1. **Upload PDF**: User uploads a document ➔ Celery worker indexes chunks via InsightForge-AI (FAISS + BM25).
2. **Generate Blueprint**: LLM generates course outline (Lessons ➔ Topics ➔ Subtopics) with status `PENDING`.
3. **On-Demand Lesson Generation**: User clicks a lesson ➔ Backend retrieves RAG context chunks ➔ LLM generates Markdown content ➔ Cached in DB as `v1` (`READY`).
4. **Interactive Learning**: User reads lesson with GFM formatting, code highlighting, and progress tracking.
5. **AI Tutor Q&A**: User opens Ask AI Tutor panel ➔ Scoped LLM prompt answers questions using active lesson Markdown context.

---

## 📁 Repository Structure

```
courseforge/
├── backend/
│   ├── api/                  # FastAPI Endpoints & Pydantic Schemas
│   │   ├── auth/             # Login, Registration, JWT Auth
│   │   ├── courses/          # Course CRUD & Blueprint Generation
│   │   ├── documents/        # PDF Upload & Processing Status
│   │   ├── lessons/          # On-Demand Generation, Progress, AI Tutor
│   │   └── search/           # Hybrid Document Search
│   ├── core/                 # App Settings, Security, Exceptions, Middleware
│   ├── db/                   # Async SQLAlchemy Models & Alembic Migrations
│   │   └── models/           # User, Course, Document, Lesson, Topic, Progress
│   ├── insightforge/         # RAG Engine Adapter (FAISS + BM25 Shim)
│   ├── llm/                  # PromptManager Templates & Pydantic Schemas
│   ├── services/             # Business Logic (CourseGenerator, LessonGenerator, Tutor)
│   ├── tasks/                # Celery Background Worker Tasks
│   └── tests/                # Pytest Test Suites (16/16 Passing)
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios Client & React Query Hooks
│   │   ├── components/
│   │   │   ├── layout/       # AppLayout, TopBar, Sidebar
│   │   │   ├── lesson/       # LessonSidebar, LessonHeader, LessonTutorPanel
│   │   │   └── ui/           # Button, Card, Input, Modal, MarkdownViewer, States
│   │   ├── pages/            # Landing, Login, Register, Dashboard, CourseDetail, LessonViewer
│   │   ├── router/           # React Router v6 Client Router
│   │   ├── store/            # Zustand Stores (useAuthStore, useUIStore, useNotificationStore)
│   │   └── test/             # Vitest Test Suites (11/11 Passing)
│   └── index.css             # Vanilla CSS Design System Tokens
├── docs/                     # Documentation & Architecture Guides
│   ├── architecture/         # System Architecture, Database Schema, API Reference
│   ├── demo_script.md        # 2–4 Minute Demonstration Script
│   └── portfolio_showcase.md # Resume & LinkedIn Portfolio Descriptions
├── docker/                   # Docker Compose & Container Configs
├── pyproject.toml            # Backend Dependencies & Pytest Configuration
└── README.md
```

---

## 🛠️ Technology Stack

- **Frontend**: React 18, Vite, React Router v6, `@tanstack/react-query`, Zustand, Vanilla CSS, `react-markdown`, `remark-gfm`, `rehype-highlight`, `highlight.js`, Lucide Icons.
- **Backend**: FastAPI, Async SQLAlchemy 2.0, Alembic, Pydantic v2, Python 3.11+, PyJWT, Passlib (bcrypt).
- **Database**: PostgreSQL (via `asyncpg`).
- **Async Tasks & Caching**: Celery, Redis.
- **RAG & AI Engine**: InsightForge-AI Engine (FAISS vector store + BM25 keyword ranker), Groq LLM API (`llama-3.3-70b-versatile`).

---

## 🚀 Installation & Setup Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Redis server (local or Docker)
- PostgreSQL database (optional for dev; SQLite fallback supported)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/courseforge/courseforge.git
cd courseforge

# Setup Python Virtual Environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Environment Configuration
Copy the template configuration to `backend/.env`:
```bash
cp .env.example backend/.env
```
Edit `backend/.env` to configure your PostgreSQL credentials, Redis host, `JWT_SECRET_KEY`, and `GROQ_API_KEY`.

### 3. Database Migration
```bash
cd backend
alembic upgrade head
```

### 4. Start Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8001
```
Visit Swagger API documentation at: `http://localhost:8001/api/docs`

### 5. Start Celery Worker (New Terminal)
```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```

### 6. Start Frontend Development Server (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## 🔌 API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/auth/register` | `POST` | Register new user account |
| `POST /api/v1/auth/login` | `POST` | Authenticate user & issue JWT tokens |
| `GET /api/v1/courses` | `GET` | List all user enrolled courses |
| `POST /api/v1/courses` | `POST` | Create new course |
| `POST /api/v1/documents/upload` | `POST` | Upload PDF and trigger Celery indexing |
| `POST /api/v1/courses/{id}/generate` | `POST` | Generate course blueprint syllabus |
| `GET /api/v1/courses/{id}/lessons/{lesson_id}` | `GET` | Fetch or on-demand generate lesson Markdown |
| `POST /api/v1/courses/{id}/lessons/{lesson_id}/regenerate` | `POST` | Force regenerate lesson content (`v1` ➔ `v2`) |
| `POST /api/v1/courses/{id}/lessons/{lesson_id}/progress` | `POST` | Update user progress & reading duration |
| `POST /api/v1/courses/{id}/lessons/{lesson_id}/ask` | `POST` | Ask a question to the AI Lesson Tutor |

---

## 🧪 Testing

Run backend Pytest suite:
```bash
cd backend
pytest --no-cov
# Output: 16 passed in 1.62s
```

Run frontend Vitest suite:
```bash
cd frontend
npm test -- --watch=false
# Output: 11 passed in 7.17s
```

Build production bundle:
```bash
cd frontend
npm run build
# Output: 2206 modules transformed, 0 errors.
```

---

## 📄 License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.
