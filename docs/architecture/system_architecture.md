# CourseForge AI — System Architecture Specification

## Overview
CourseForge AI is an interactive learning platform that automatically converts uploaded PDF documents into multi-tier educational courses using Retrieval-Augmented Generation (RAG).

---

## High-Level Component Diagram

```mermaid
flowchart TB
    subgraph Client Layer
        Web[React 18 SPA + Vite]
        Router[React Router v6]
        RQ[React Query State Manager]
        Zustand[Zustand Local Stores]
    end

    subgraph API & Service Layer
        FastAPI[FastAPI ASGI Application]
        AuthSvc[JWT Auth & Security]
        CourseSvc[Course Generator Service]
        LessonSvc[Lesson Generator Service]
        TutorSvc[Lesson Tutor Service]
    end

    subgraph Data & Storage Layer
        Postgres[(PostgreSQL Database)]
        Redis[(Redis Task Broker / Cache)]
        Uploads[Local PDF Storage]
    end

    subgraph RAG & AI Layer
        Celery[Celery Async Workers]
        InsightForge[InsightForge-AI Adapter]
        FAISS[FAISS Vector Store]
        BM25[BM25 Ranker]
        LLM[Groq LLM Engine]
    end

    Web -->|HTTP / JSON| FastAPI
    FastAPI --> AuthSvc
    FastAPI --> CourseSvc
    FastAPI --> LessonSvc
    FastAPI --> TutorSvc
    
    CourseSvc --> Postgres
    LessonSvc --> Postgres
    TutorSvc --> InsightForge
    
    FastAPI -->|Enqueue Task| Redis
    Redis --> Celery
    Celery --> Uploads
    Celery --> InsightForge
    
    InsightForge --> FAISS
    InsightForge --> BM25
    InsightForge --> LLM
```

---

## Architectural Principles & Patterns

1. **Async-First Execution**: Non-blocking I/O throughout FastAPI async routes and SQLAlchemy async sessions (`asyncpg`).
2. **On-Demand Lazy Generation**: Course outlines are generated first; individual lesson Markdown is generated lazily when opened by the user, saving memory and LLM API costs.
3. **Dual-Layer Caching**: Generated lessons are stored in PostgreSQL (`Lesson.content_markdown`). Subsequent requests return cached Markdown immediately without invoking LLM inference.
4. **Adapter Pattern for RAG**: The `InsightForgeEngine` class abstracts the underlying InsightForge-AI engine (FAISS + BM25 hybrid search), shielding CourseForge business logic from LLM/RAG internal changes.
5. **Decoupled Task Processing**: Heavy operations (PDF parsing, chunking, indexing) run out-of-band on Celery task workers backed by Redis.
