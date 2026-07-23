# CourseForge AI

> Transform complex PDF documents into structured, interactive courses powered by hybrid RAG and high-speed LLM inference.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB.svg?logo=react)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Async-4169E1.svg?logo=postgresql)](https://neon.tech)
[![Groq](https://img.shields.io/badge/LLM-Groq_Llama_3.3_70B-f05032.svg)](https://groq.com)

CourseForge AI is an end-to-end learning management and course generation platform that converts static PDF textbooks and technical documents into interactive, structured educational courses. Utilizing a high-performance synchronous FastAPI backend, Neon PostgreSQL for persistent state, SentenceTransformers (`all-MiniLM-L6-v2`) for local embeddings, FAISS + BM25 for hybrid vector retrieval via InsightForge RAG, and Groq (`llama-3.3-70b-versatile`) for ultra-fast LLM inference, CourseForge AI automatically extracts document context and crafts multi-tiered course syllabi, interactive markdown lessons, quizzes, flashcards, and personalized study roadmaps.

---

## 🚀 Features

* **AI-Powered Course Generation**: Automatically synthesizes complete course blueprints (lessons, topics, subtopics) from uploaded documents.
* **PDF Upload & Validation**: Secure streaming upload supporting file size limits, MIME type verification, and PDF magic byte (`%PDF-`) validation.
* **InsightForge RAG Engine**: Leverages hybrid retrieval combining FAISS vector similarity search and BM25 keyword matching for context-rich generation.
* **Local Embedding Engine**: Generates dense vector embeddings locally using `SentenceTransformer` (`all-MiniLM-L6-v2`) for zero external embedding costs.
* **Ultra-Fast LLM Inference**: Powered by Groq's LLaMA-3.3-70B model for near-instant syllabus and lesson generation.
* **Real-Time Stage Progress Tracking**: Granular stage reporting (`uploading_pdf` ➔ `extracting_text` ➔ `chunking_document` ➔ `generating_embeddings` ➔ `building_search_index` ➔ `generating_course_blueprint` ➔ `saving_course` ➔ `completed`) via lightweight REST endpoints.
* **Robust JWT Authentication**: Secure user registration, password hashing with bcrypt, access/refresh token lifecycle, and role-aware routes.
* **Interactive Learning Suite**: Complete interactive workspace including Markdown lesson rendering, AI lesson tutor chat, quizzes, flashcard reviews, and daily study planning.
* **Production Observability**: Request correlation (`X-Request-ID`), stage timing metrics (`X-Processing-Time-ms`), structured JSON logs, and health probes (`/health`, `/ready`, `/metrics`).
* **Optimized Synchronous Pipeline**: Single-process architecture engineered to eliminate external queue dependencies while achieving sub-3-second end-to-end course generation.

---

## 🏗️ Architecture

CourseForge AI operates on a streamlined, synchronous single-process architecture designed for speed, stability, and zero background worker complexity.

```mermaid
flowchart TD
    Client["Vercel Frontend (React + Vite)"]
    
    subgraph FastAPI ["FastAPI Synchronous Backend (Render)"]
        API["REST API Router & Middleware"]
        Auth["JWT Security & Auth Handler"]
        Progress["Progress & Metrics Tracker"]
        
        subgraph Engine ["InsightForge RAG Engine (Singleton)"]
            Extract["PyPDF Parser & Token Chunking"]
            Embed["SentenceTransformers (all-MiniLM-L6-v2)"]
            FAISS["FAISS Dense Vector Index"]
            BM25["BM25 Keyword Indexer"]
        end
        
        Generator["Course Blueprint Generator"]
    end
    
    Groq["Groq Cloud API (LLaMA 3.3 70B)"]
    DB[("Neon Serverless PostgreSQL")]

    Client -->|HTTPS / REST API| API
    API --> Auth
    API --> Progress
    API --> Generator
    Generator --> Engine
    Engine --> Extract
    Extract --> Embed
    Embed --> FAISS
    Extract --> BM25
    Generator -->|Prompt Context| Groq
    Groq -->|Generated Blueprint JSON| Generator
    Generator -->|Batch SQL Commit| DB
```

---

## 🛠️ Technology Stack

### Frontend
* **Framework**: React 18.3.1 + Vite 5.4.2
* **Styling**: Modern Vanilla CSS Design System with dark mode support
* **Icons & UI**: Lucide React 0.446.0, React Router DOM 6.26.2
* **State & Query**: TanStack React Query 5.56.2, Zustand 5.0.0
* **HTTP Client**: Axios 1.7.7

### Backend
* **Framework**: Python 3.13 + FastAPI 0.115.0 (ASGI via Uvicorn)
* **ORM & Database**: SQLAlchemy 2.0.35 + Asyncpg 0.29.0
* **Security & Auth**: PyJWT 2.9.0, Passlib (bcrypt 4.2.0), Pydantic 2.8.2
* **Rate Limiting**: SlowAPI 0.1.9

### AI & RAG Engine
* **RAG Framework**: InsightForge AI Adapter Integration
* **Embeddings**: SentenceTransformers 3.1.1 (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Index**: FAISS CPU 1.8.0.post1 + Rank-BM25 0.2.2
* **LLM Engine**: Groq API Client (`groq==0.11.0`, model: `llama-3.3-70b-versatile`)

### Database & Persistence
* **Database**: Neon PostgreSQL (Serverless Async Driver)

### Infrastructure & Deployment
* **Backend Host**: Render (FastAPI Web Service)
* **Frontend Host**: Vercel
* **Containerization**: Docker / OCI Compliant Container Build

---

## 📁 Project Structure

```text
2-2/pro/
├── backend/                  # FastAPI Backend Application
│   ├── api/                  # REST Router Endpoints
│   │   ├── auth/             # Login, Register, Refresh Token routes
│   │   ├── courses/          # Course CRUD, generation & progress routes
│   │   ├── documents/        # PDF upload, document indexing & progress routes
│   │   ├── health.py         # Liveness (/health), Readiness (/ready), Metrics (/metrics)
│   │   └── ...               # Lessons, Quizzes, Flashcards, Search, Analytics
│   ├── core/                 # Core Framework Infrastructure
│   │   ├── config.py         # Pydantic Settings & environment validation
│   │   ├── middleware.py     # CORS, Security Headers, X-Request-ID & logging
│   │   ├── progress.py       # Real-time progress stage registry & timing metrics
│   │   └── security.py       # JWT token generation & bcrypt password hashing
│   ├── db/                   # Database Layer
│   │   ├── models/           # SQLAlchemy Declarative Models (Course, Document, Lesson, etc.)
│   │   └── session.py        # Asyncpg Database session factory
│   ├── insightforge/         # RAG Engine Integration
│   │   ├── adapter.py        # InsightForge low-level RAG binding
│   │   └── engine.py         # Thread-safe Singleton InsightForgeEngine
│   ├── llm/                  # Large Language Model Utilities
│   │   ├── prompt_manager.py # Versioned prompt templates
│   │   └── schemas.py        # Pydantic JSON schemas for structured LLM outputs
│   ├── services/             # Domain Logic & Course Generation Services
│   │   ├── course_generator.py # Synchronous blueprint generation service
│   │   └── ...               # Quiz, Flashcard, Study Planner services
│   ├── tasks/                # Synchronous Pipeline Task Executors
│   │   └── document_tasks.py # Document parsing & indexing workflow
│   ├── tests/                # Automated Pytest Test Suite
│   ├── main.py               # FastAPI App Factory & Lifespan handler
│   └── requirements.txt      # Backend Python Dependencies
├── frontend/                 # React + Vite Frontend Application
│   ├── src/                  # React Source Code (Components, Pages, Hooks, Store)
│   ├── package.json          # Node.js Dependencies & Scripts
│   └── vite.config.js        # Vite Build Configuration
└── README.md                 # Project Documentation
```

---

## ⚡ Quick Start & Installation

### Prerequisites
* **Python**: `3.11` or `3.13`
* **Node.js**: `v18.x` or `v20.x`
* **PostgreSQL**: Neon Cloud PostgreSQL or local PostgreSQL instance
* **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com)

### 1. Clone Repository
```bash
git clone https://github.com/varshith-yakkala/CourseForge-AI.git
cd CourseForge-AI
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create local environment configuration
cp .env.example .env
```

Configure your `backend/.env` with your Neon PostgreSQL URI and Groq API key:
```env
APP_ENV=development
APP_SECRET_KEY=e837f44d5c90b6a98ef11b3329188172c7b399220914e91845bb0e68d18471b0
JWT_SECRET_KEY=9499d3632ab3e88fa2b1308a0d7831d102e3b2e616f72922ef6a47a1622aa590
DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-host.neon.tech/dbname?ssl=require
GROQ_API_KEY=gsk_your_groq_api_key_here
```

Run database migrations:
```bash
python -c "from main import app"
```

Start backend server:
```bash
uvicorn main:app --reload --port 8001
```

### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔐 Environment Variables

| Variable | Type | Description | Default / Example |
|---|---|---|---|
| `APP_ENV` | `string` | Environment state (`development`, `production`, `testing`) | `development` |
| `APP_PORT` | `integer` | Backend server port | `8001` |
| `APP_SECRET_KEY` | `string` | Cryptographic secret key for session signing (64-hex) | Required |
| `JWT_SECRET_KEY` | `string` | Cryptographic secret key for signing JWT tokens (64-hex) | Required |
| `DATABASE_URL` | `string` | Neon PostgreSQL async connection string | `postgresql+asyncpg://...` |
| `GROQ_API_KEY` | `string` | API Key for Groq Cloud LLM Inference | Required (`gsk_...`) |
| `GROQ_MODEL` | `string` | Target LLM model name | `llama-3.3-70b-versatile` |
| `UPLOAD_DIR` | `string` | Local disk directory for temporary file storage | `./uploads` |
| `MAX_UPLOAD_SIZE_MB` | `integer` | Maximum allowable PDF upload size in megabytes | `50` |
| `CORS_ORIGINS` | `string` | Comma-separated list of allowed CORS origins | `http://localhost:5173` |

---

## 📡 API Reference Summary

### Authentication Endpoints
* `POST /api/v1/auth/register` — Register a new user account.
* `POST /api/v1/auth/login` — Authenticate credentials and issue JWT access/refresh tokens.
* `POST /api/v1/auth/refresh` — Refresh expired access tokens.

### Document Management
* `POST /api/v1/documents/upload` — Securely stream PDF upload & trigger synchronous indexing.
* `GET /api/v1/documents/{document_id}` — Get document metadata and indexing status.
* `GET /api/v1/documents/{document_id}/progress` — Get real-time document indexing stage progress.

### Course Management
* `POST /api/v1/courses` — Create a new empty course container.
* `POST /api/v1/courses/{course_id}/generate` — Synchronously generate complete course blueprint from indexed document.
* `GET /api/v1/courses/{course_id}/structure` — Get nested course tree (`Lessons` ➔ `Topics` ➔ `Subtopics`).
* `GET /api/v1/courses/{course_id}/progress` — Get real-time blueprint generation stage progress.

### System & Monitoring
* `GET /api/v1/health` — Liveness probe for container orchestrators.
* `GET /api/v1/ready` — Deep readiness probe verifying PostgreSQL, Groq API, and RAG status.
* `GET /api/v1/metrics` — Resource usage metrics (RAM, CPU, Uptime).

---

## 📊 Performance & Optimization Results

Through architectural refactoring and synchronous pipeline optimization, end-to-end course generation latency was reduced by **43.4%**:

```text
Before Optimization:  ██████████████████████████████  4.31 seconds
After Optimization:   █████████████████              2.44 seconds (43.4% faster)
```

### Key Technical Optimizations
1. **Singleton Engine Architecture**: Enforced a thread-safe Singleton pattern (`InsightForgeEngine.__new__`), avoiding repeated loading of SentenceTransformer embedding models and RAG adapters per request.
2. **Client-Side UUID Pre-Generation**: Generated entity primary keys (`uuid.uuid4()`) client-side to replace 25+ intermediate `db.flush()` network roundtrips inside nested loops with a single batch `db.add_all()` and 1 atomic `db.commit()`.
3. **Non-Blocking Thread Delegation**: Offloaded CPU-heavy FAISS vector indexing and embedding creation off the FastAPI async event loop via `asyncio.to_thread`.

---

## 🛡️ Production Security & Quality Engineering

* **Request Tracing**: Automated `X-Request-ID` generation and log correlation.
* **Secure Error Boundaries**: System exceptions are logged with complete stack traces internally while returning sanitized, friendly error messages to HTTP clients.
* **Sanitized Startup Logging**: Clean startup reporting of environment settings and component health without exposing secrets or connection strings.
* **Strict Validation**: PDF magic byte checking (`%PDF-`), streaming size caps (50 MB), and Pydantic schema validation.

---

## 🖼️ Application Showcase

### Dashboard & Course Overview
> ![Dashboard Overview](https://raw.githubusercontent.com/varshith-yakkala/CourseForge-AI/main/docs/images/dashboard.png)  
> *Personalized learning dashboard displaying course progress, active streak, and AI coach recommendations.*

### Document Upload & Real-Time Progress
> ![Document Upload Progress](https://raw.githubusercontent.com/varshith-yakkala/CourseForge-AI/main/docs/images/upload_progress.png)  
> *Streamed PDF upload with real-time stage progress reporting.*

### Interactive Generated Course Workspace
> ![Course Workspace](https://raw.githubusercontent.com/varshith-yakkala/CourseForge-AI/main/docs/images/course_view.png)  
> *Structured course view displaying generated lessons, topics, subtopics, and integrated AI tutor.*

---

## 🔮 Future Roadmap

* 🔄 **Redis Response Caching**: Optional read-through caching layer for high-frequency search queries.
* 🌊 **Server-Sent Events (SSE)**: Streaming LLM token responses for live lesson generation.
* 📚 **Multi-Document Synthesis**: Merging multiple PDFs into a single unified master course.
* 👥 **Collaborative Workspace**: Shared courses and team study group analytics.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the Repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit changes (`git commit -m 'Add AmazingFeature'`).
4. Push to branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## ✉️ Author & Contact

**Varshith Yakkala**  
* GitHub: [@varshith-yakkala](https://github.com/varshith-yakkala)  
* Project Repository: [CourseForge-AI](https://github.com/varshith-yakkala/CourseForge-AI)

---

## 🙏 Acknowledgements

* [Groq](https://groq.com) for ultra-fast LLaMA-3.3-70B LLM inference.
* [SentenceTransformers](https://www.sbert.net/) for local dense embeddings (`all-MiniLM-L6-v2`).
* [FAISS](https://github.com/facebookresearch/faiss) for high-efficiency vector similarity search.
* [FastAPI](https://fastapi.tiangolo.com) for modern, fast Python web APIs.
* [Neon](https://neon.tech) for serverless async PostgreSQL.
* [React](https://react.dev) for frontend UI rendering.
