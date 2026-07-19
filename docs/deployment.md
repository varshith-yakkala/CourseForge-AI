# CourseForge AI — Production Deployment Guide

This guide details instructions for deploying CourseForge AI (v1.0.0) across cloud environments.

---

## 🐋 1. Local / Self-Hosted Docker Compose Deployment

The simplest way to run CourseForge AI in production is via Docker Compose.

### Prerequisites
- Docker Engine v20.10+
- Docker Compose v2.0+

### One-Command Startup

```bash
# Clone the repository
git clone https://github.com/varshith-yakkala/CourseForge-AI.git
cd CourseForge-AI

# Launch all production services
docker-compose up -d --build
```

Services started:
- `courseforge-postgres`: PostgreSQL 15 database on port 5432.
- `courseforge-redis`: Redis 7 broker on port 6379.
- `courseforge-backend`: FastAPI backend server on port 8000.
- `courseforge-celery-worker`: Celery background job worker.
- `courseforge-frontend`: React static app served by Nginx on port 80.

---

## ☁️ 2. Deployment on Render / Railway / Fly.io

### Render Setup
1. **PostgreSQL**: Create a Managed PostgreSQL Database.
2. **Redis**: Create a Managed Redis Instance.
3. **Backend Service**:
   - Environment: Docker (using `backend/Dockerfile`)
   - Build Context: `backend/`
   - Set environment variables (`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`).
4. **Frontend Service**:
   - Environment: Static Site or Docker (using `frontend/Dockerfile`).

---

## 🔒 3. Environment Variables Reference

| Variable | Description | Default / Example |
|----------|-------------|-------------------|
| `APP_ENV` | Application environment (`development`, `production`) | `production` |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection URL | `redis://host:6379/0` |
| `JWT_SECRET` | Secret key for signing JWT tokens | `<strong-secret-key>` |
| `INSIGHTFORGE_PATH` | (Optional) Path to external InsightForge RAG Engine override | Unset (uses bundled internal engine) |
