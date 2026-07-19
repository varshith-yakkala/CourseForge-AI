# CourseForge AI — 2–4 Minute Video Demo Script

This script provides a step-by-step walkthrough for demonstrating CourseForge AI in portfolio videos, recruiter demos, or live presentations.

---

## 🎬 Demo Overview
- **Total Duration**: 3 Minutes 30 Seconds
- **Target Audience**: Technical Recruiters, Software Engineers, Product Managers
- **Key Message**: CourseForge AI transforms static PDF documents into an interactive, structured, AI-tutored learning platform using RAG and modern web engineering.

---

## ⏱️ Walkthrough & Narration Timeline

### 0:00 – 0:30 | Introduction & Landing Page
**Visual**: Start on the dark-mode Landing Page (`http://localhost:5173`). Mouse hovers over hero CTA buttons ("Get Started", "Log In").

**Narration**:
> *"Hi everyone! Welcome to CourseForge AI — an intelligent learning platform designed to solve a major problem in self-directed learning: turning dense, static PDF documents into structured, interactive courses.*
>
> *Built with FastAPI, React 18, PostgreSQL, Redis, and a custom RAG (Retrieval-Augmented Generation) adapter powered by InsightForge-AI, CourseForge automatically handles document indexing, syllabus generation, on-demand lesson writing, and scoped AI tutoring."*

---

### 0:30 – 1:00 | Authentication & Dashboard
**Visual**: Click "Log In". Enter credentials (`user@example.com` / `password123`). Submit form. Show instant toast notification and seamless redirect to `/dashboard`. Show course cards grid and progress bars.

**Narration**:
> *"Let's log into our account. Authentication is secured using JWT bearer tokens with bcrypt password hashing.
> 
> Here on the Dashboard, users can see all their enrolled courses, progress completion percentages, and status badges. Let's create a new course."*

---

### 1:00 – 1:45 | PDF Upload & Course Blueprint Generation
**Visual**: Click "+ Create Course". Enter course title ("Advanced Python Data Structures"). Drag & drop a PDF document into the modal dropzone. Upload progress bar animates to 100%. Redirect to Course Detail Page. Click "Generate Course Blueprint". Show loading state as Celery worker and Groq LLM generate syllabus structure.

**Narration**:
> *"When we upload a PDF, the backend validates MIME types and triggers a background Celery task. The InsightForge RAG engine chunks the document and indexes it using FAISS vector search and BM25 keyword rankers.
> 
> Next, when we click 'Generate Course Blueprint', our LLM analyzes the document fragments to construct a multi-tier course outline — complete with Lessons, Topics, Subtopics, and Key Terms. Notice how initial lessons are created in a `PENDING` state to conserve tokens until the user actually opens them."*

---

### 1:45 – 2:30 | On-Demand Lesson Generation & Markdown Reader
**Visual**: In `CourseDetailPage`, click "Start Lesson" on Lesson 1 ("Memory Management & References"). Page navigates to `/learn/:courseId/:lessonId`. The viewer shows the `PENDING` state card ("Ready to Learn"). Click "Generate Lesson Content". Show spinner status transitioning to `READY`. The full Markdown lesson renders with headers, tables, callout notes, and code blocks. Scroll through Python code snippet with dark syntax highlighting.

**Narration**:
> *"Here in our interactive Lesson Viewer, lesson generation happens strictly on-demand. When I click 'Generate Lesson Content', CourseForge queries InsightForge for relevant context chunks and passes them to our Groq LLM prompt.
> 
> In just a couple of seconds, the LLM produces a rich, multi-section lesson in GitHub-Flavored Markdown. Our custom renderer formats headers, learning objectives, reading time badges, tables, and auto-highlights code blocks for Python, JavaScript, SQL, and more.
> 
> Crucially, this lesson is now cached in PostgreSQL as Version 1. If I refresh or re-open this page, it loads instantaneously with zero LLM API calls!"*

---

### 2:30 – 3:10 | Scoped AI Lesson Tutor & Progress Tracking
**Visual**: Click "Ask AI Tutor" in the top header. Slide-over panel opens. Type a question ("Can you explain garbage collection in simple terms?"). Press Send. AI Tutor responds with Markdown formatted answer. Next, click "Complete & Continue" at bottom right. Toast notification pops up ("Lesson Completed!"). Header progress bar updates from 50% to 100%. Sidebar shows green checkmark icon next to Lesson 1.

**Narration**:
> *"If a student has a question while reading, they can open the 'Ask AI Tutor' panel. Unlike generic chatbots, CourseForge constrains the tutor's prompt strictly to the current lesson's Markdown text and document RAG chunks — ensuring zero hallucinated answers outside the lesson scope.
> 
> Finally, when the user finishes reading and clicks 'Complete & Continue', learning progress metrics — including completion percentage, timestamp, and reading duration — are saved in PostgreSQL, surviving page refreshes and logins across all devices."*

---

### 3:10 – 3:30 | Conclusion & Architecture Summary
**Visual**: Switch to split-screen showing VS Code repository and terminal with 100% test suite passing (27/27 tests).

**Narration**:
> *"CourseForge AI is built with production standards in mind — clean separation of concerns, modular services, background Celery workers, dual-layer caching, and full test coverage with 27 passing tests across FastAPI Pytest and React Vitest.
> 
> Thank you for watching! Check out the GitHub link below for full setup instructions and documentation."*

---

## 📋 Pre-Demo Checklist
- [x] Backend running on `http://localhost:8001`
- [x] Redis server running on `localhost:6379`
- [x] Celery worker active (`celery -A tasks.celery_app worker --pool=solo`)
- [x] Frontend dev server running on `http://localhost:5173`
- [x] Sample PDF document (`python_data_structures.pdf`) ready on desktop for upload demonstration.
