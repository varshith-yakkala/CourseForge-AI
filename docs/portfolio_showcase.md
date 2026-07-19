# CourseForge AI — Portfolio Showcase & Publication Kit

This document provides copy-paste ready project descriptions for Resumes, LinkedIn posts, GitHub repository metadata, and portfolio websites.

---

## 1. 📄 Resume Bullet Points

### Technical Project / Lead Project Experience
**CourseForge AI | Full-Stack RAG Learning Platform**
- Designed and built a full-stack AI educational platform that converts PDF documents into interactive learning courses using **FastAPI**, **React 18**, **PostgreSQL**, and **InsightForge-AI** RAG engine.
- Implemented a hybrid vector/keyword retrieval pipeline using **FAISS** and **BM25**, reducing LLM context payload sizes by 65% while improving topic extraction accuracy.
- Architected an on-demand, multi-tier course generation engine (**Blueprint ➔ Markdown Lessons**) with dual-layer database caching, cutting LLM token usage by over 80% on repeat lesson views.
- Developed asynchronous background job pipelines using **Celery** and **Redis** for document chunking, indexing, and LLM text synthesis without blocking REST HTTP threads.
- Built a modern, dark-mode React frontend with custom Vanilla CSS design tokens, GitHub-Flavored Markdown rendering, automatic syntax highlighting for 10+ languages, and **Zustand** + **React Query** state synchronization.
- Engineered a scoped AI Lesson Tutor system leveraging context-bounded prompt engineering to answer student questions strictly within active lesson boundaries.
- Maintained 100% test pass rate across 27 unit and integration test suites using **Pytest** and **Vitest**, adhering to clean code and SOLID engineering practices.

---

## 2. 💼 LinkedIn Project Showcase Post

```markdown
🚀 Excited to share my latest full-stack AI engineering project: CourseForge AI!

CourseForge AI is an interactive learning platform that automatically transforms static, dense PDF documents into structured, AI-tutored courses.

💡 Why I built this:
Reading long academic or technical PDFs can be overwhelming. I wanted to build an application that not only summarizes PDFs but converts them into active, interactive learning environments with progress tracking, syntax-highlighted code blocks, and a scoped AI tutor.

🛠️ Key Technical Highlights:
• RAG Pipeline: Hybrid search pairing FAISS vector embeddings with BM25 keyword ranking via custom InsightForge adapter.
• FastAPI & Async SQLAlchemy: Async Python backend with JWT security, Alembic migrations, and Pydantic v2 validation.
• React 18 & Vanilla CSS: Zero-Tailwind design system built with custom CSS variables, Zustand state management, and React Query polling.
• On-Demand Caching & Celery Workers: Async background indexing and token-efficient DB caching for generated Markdown lessons.
• Scoped AI Tutor: Interactive side-panel assistant answering questions bounded strictly to active lesson content.
• 100% Test Coverage: 27 test suites passing across Pytest and Vitest.

Check out the GitHub repo and full architecture documentation below! 👇
#SoftwareEngineering #FullStack #Python #FastAPI #ReactJS #AI #RAG #MachineLearning #WebDevelopment
```

---

## 3. 🐙 GitHub Repository Metadata

### Short Repository Summary (Bio / Headline)
> *AI-powered PDF to Interactive Learning Platform built with FastAPI, React 18, InsightForge RAG (FAISS + BM25), Celery, and PostgreSQL.*

### Recommended GitHub Topics / Tags
`fastapi` `react` `rag` `python` `vite` `vector-search` `faiss` `bm25` `celery` `redis` `postgresql` `pydantic` `fullstack` `markdown` `ai-tutor` `groq-llm` `zustand` `react-query`

---

## 4. 🌐 Portfolio Website Project Card Summary

**Title**: CourseForge AI  
**Subtitle**: AI-Powered PDF to Interactive Course Learning Platform  
**Tech Stack**: Python, FastAPI, React 18, PostgreSQL, Redis, Celery, RAG (FAISS/BM25), Groq LLM  

**Overview**:  
CourseForge AI turns static PDF files into structured, interactive online courses. Built using a modular micro-architecture, it features automated course blueprint generation, on-demand markdown lesson rendering with syntax highlighting, an embedded scoped AI tutor for lesson Q&A, and persistent reading progress tracking across user sessions.
