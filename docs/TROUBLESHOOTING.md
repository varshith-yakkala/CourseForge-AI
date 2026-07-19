# CourseForge AI — Troubleshooting Guide

Common issues and diagnostic solutions for running CourseForge AI.

---

## 1. Database Connection Errors (`asyncpg.exceptions`)

### Symptom
`ConnectionRefusedError` or `asyncpg.exceptions.CannotConnectNowError`.

### Solution
1. Verify PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```
2. Verify `DATABASE_URL` uses `postgresql+asyncpg://`.

---

## 2. Celery Worker Disconnected

### Symptom
Tasks remain in `PENDING` state indefinitely.

### Solution
1. Verify Redis container is healthy:
   ```bash
   docker-compose exec redis redis-cli ping
   ```
2. Restart Celery worker:
   ```bash
   docker-compose restart celery_worker
   ```

---

## 3. InsightForge Fallback Mode

### Symptom
Warning log: `[CourseForge] INSIGHTFORGE_PATH does not exist`.

### Solution
CourseForge AI automatically operates in mock/demonstration mode when InsightForge is not present locally. Set `INSIGHTFORGE_PATH` in `.env` to connect live RAG models.
