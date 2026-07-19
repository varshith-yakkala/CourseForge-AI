# CourseForge AI — Phase Changelog & Milestone History

---

## 🚀 Phase 7 — Interactive AI Learning Experience (v0.7.0)
**Completed**: July 2026

- **On-Demand Lesson Generation**: Implemented lazy generation of Markdown lessons when opened, cutting initial LLM costs.
- **Dual-Layer Caching**: Lesson Markdown is saved in PostgreSQL (`Lesson.content_markdown`), returning cached content instantly on repeat visits.
- **Lesson Status Lifecycle & Versioning**: Added lifecycle states (`PENDING`, `GENERATING`, `READY`, `FAILED`) and version counter (`v1 ➔ v2`).
- **Markdown & Syntax Highlighting**: Added `react-markdown`, `remark-gfm`, `rehype-highlight`, and `highlight.js` for 10+ code languages.
- **Interactive Lesson Viewer**: Replaced placeholder page with polished reading view featuring breadcrumbs, estimated reading time, progress bar, table of contents, and footer navigation.
- **Ask About This Lesson AI Tutor**: Slide-over AI panel providing scoped Q&A restricted to active lesson Markdown & RAG context.
- **Progress Tracking**: Persisted reading duration, started/completed flags, scroll position, and overall course progress percentage.
- **Test Suites**: Added service and API unit/integration tests (16 Pytest backend + 11 Vitest frontend tests = 27 total passing tests).

---

## 🛠️ Phase 6 — AI Course Generation Engine (v0.6.0)
- Synthesized Course Blueprint syllabus (Lessons ➔ Topics ➔ Subtopics ➔ Key Terms) using Groq LLM and InsightForge RAG context.
- Configured initial course database models and schema relationships.

---

## 📄 Phase 5 — InsightForge RAG Integration (v0.5.0)
- Implemented `InsightForgeEngine` adapter shim for hybrid FAISS vector search and BM25 keyword ranking.
- Integrated Celery background tasks for async PDF document parsing and indexing.

---

## 🎨 Phase 3–4 — Frontend Design System & Course Management (v0.4.0)
- Built Vanilla CSS design token system (dark mode, glassmorphism, responsive typography).
- Built Dashboard, Course Cards, PDF Upload Modal, and Navigation Shell.

---

## 🔒 Phase 1–2 — Architecture, DB & Authentication (v0.2.0)
- Initialized FastAPI ASGI app structure, CORS middleware, structured JSON logging.
- Configured Async SQLAlchemy 2.0, Alembic migrations, PostgreSQL, and JWT HS256 authentication.
