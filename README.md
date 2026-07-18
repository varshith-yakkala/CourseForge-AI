# CourseForge

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18.x-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Last Commit](https://img.shields.io/github/last-commit/courseforge/courseforge)
![Stars](https://img.shields.io/github/stars/courseforge/courseforge?style=social)

CourseForge is an AI-powered educational platform designed to automatically transform any uploaded PDF document into a structured, highly interactive learning course. Built with a focus on modern aesthetics, production-ready architecture, and seamless AI integration.

## Features

- **Automated Course Generation**: Upload a PDF and let CourseForge extract context, draft an outline, and structure lessons automatically.
- **InsightForge-AI Integration**: Uses a custom RAG (Retrieval-Augmented Generation) adapter with Celery background tasks for hybrid FAISS + BM25 document indexing.
- **Robust Architecture**: Built with FastAPI, SQLAlchemy, and PostgreSQL on the backend.
- **Modern UI**: A responsive, dynamic, and beautiful interface built in React/Vite using a bespoke Vanilla CSS design system (no Tailwind).
- **Asynchronous Processing**: Background document ingestion and course generation using Celery and Redis to keep the UI snappy.
- **Secure Authentication**: Complete JWT-based authentication system.

## Architecture & System Design
For a deep dive into the design patterns, please refer to the documentation:
- [System Architecture](docs/architecture.md)
- [System Design](docs/system-design.md)
- [Future Roadmap](docs/roadmap.md)

## Technology Stack

- **Frontend**: React 18, Vite, React Query, React Router, Vanilla CSS, Lucide Icons.
- **Backend**: FastAPI, SQLAlchemy (Async), Alembic, Pydantic, Python 3.11+.
- **Database**: PostgreSQL (via asyncpg).
- **Background Jobs**: Celery, Redis.
- **AI / ML**: InsightForge Engine (Local Document Processor).

## Folder Structure

```
courseforge/
├── backend/
│   ├── api/           # FastAPI Routes & Schemas
│   ├── core/          # Configs, Security, Exceptions
│   ├── db/            # SQLAlchemy Models, Session, Alembic
│   ├── insightforge/  # RAG Adapter
│   ├── llm/           # PromptManager & Schemas
│   ├── services/      # Business Logic
│   ├── tasks/         # Celery Worker Tasks
│   └── tests/         # Pytest test suites
├── frontend/
│   ├── src/
│   │   ├── api/       # Axios & React Query Hooks
│   │   ├── components/# Reusable UI Components
│   │   ├── pages/     # Page Views
│   │   ├── store/     # Zustand Global State
│   │   └── utils/     # Helpers
│   └── index.css      # Core Design System
├── docs/              # Extended Documentation
├── .github/           # GitHub Templates & Workflows
└── ...
```

## Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/courseforge/courseforge.git
cd courseforge
```

### 2. Environment Variables
Copy the `.env.example` file and configure it:
```bash
cp .env.example .env
```
*Ensure you update the `DATABASE_URL` and `REDIS_URL` to match your local setup.*

### 3. Database Setup (PostgreSQL)
Ensure PostgreSQL is running locally, then run the Alembic migrations:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

### 4. Running the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Running Celery & Redis
Start your local Redis instance. Then, in a new terminal window, start the Celery worker:
```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info --pool=solo
```
*(Note: `--pool=solo` is recommended for Windows development. Use `prefork` on Linux/macOS).*

### 6. Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173` to view the application.

## API Overview
The backend provides a comprehensive OpenAPI specification. Once running, visit `http://localhost:8000/docs` to view and interact with the Swagger UI.

## Current Progress (v0.6.0)
- **Phase 1**: Foundation & Architecture ✅
- **Phase 2**: Database & Authentication ✅
- **Phase 3**: Frontend Design System & App Shell ✅
- **Phase 4**: Dashboard & Course Management ✅
- **Phase 5**: InsightForge Integration & Document Processing ✅
- **Phase 6**: AI Course Generation Engine (Blueprint) ✅

## Contributing
We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](.github/CODE_OF_CONDUCT.md).

## License
This project is licensed under the [MIT License](LICENSE).
