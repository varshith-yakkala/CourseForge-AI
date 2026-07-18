# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.6.0] - 2026-07-18

### Added
- **Phase 6: AI Course Generation Engine (Blueprint)**
  - `PromptManager` implementation for strict versioned LLM prompt orchestration.
  - `CourseGeneratorService` to convert extracted document context into educational structures.
  - Pydantic models for ensuring generated LLM JSON structural integrity.
  - Asynchronous background Celery task `generate_course_task`.
  - Frontend polling and real-time generation status visualization in `CourseDetailPage`.
- **Phase 5: InsightForge Integration & Document Processing**
  - Adapter connection to `InsightForge-AI` for automated document ingestion.
  - Celery background pipeline for large PDF processing and indexing.
  - Hybrid FAISS + BM25 Search API over chunks.
  - Retry capabilities for failed ingestion pipelines.
- **Phase 4: Dashboard & Course Management**
  - E2E frontend state management with React Query.
  - Robust routing and protected layouts.
  - Backend PDF file ingestion capabilities.
  - End-to-end Course CRUD operations.
- **Phase 3: Frontend Design System & Application Shell**
  - Foundational styling structure (Light/Dark themes).
  - Robust reusable React component library (Buttons, Modals, Forms, Inputs, Alerts).
  - Modern typography and micro-animations for an elevated user experience.
- **Phase 2: Database & Authentication**
  - PostgreSQL Database architecture with Alembic migrations.
  - Complete SQLAlchemy ORM models (Courses, Lessons, Documents, Topics).
  - JWT token-based robust authentication system.
- **Phase 1: Foundation & Architecture**
  - Core FastAPI backend structure and configurations.
  - React + Vite + Vanilla CSS frontend boilerplate.
  - Base monolithic setup.
