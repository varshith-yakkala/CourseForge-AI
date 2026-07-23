import sys
import os
import logging

# Force SQLite for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from fastapi.testclient import TestClient
from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_startup")

if __name__ == "__main__":
    logger.info("Initializing TestClient to trigger lifespan with SQLite...")
    try:
        with TestClient(app) as client:
            logger.info("Application started successfully! Lifespan completed.")
            # We can also hit the health endpoint
            resp = client.get("/api/v1/health")
            logger.info(f"Health check status: {resp.status_code}")
            sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)
