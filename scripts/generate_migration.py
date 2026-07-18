import sys
import os

# Add backend to sys.path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

# Mock InsightForge imports so our config loads without InsightForge-AI
import sys
from unittest.mock import MagicMock
sys.modules['insightforge'] = MagicMock()
sys.modules['insightforge.engine'] = MagicMock()

from alembic.config import Config
from alembic import command
from db.base import Base
import db.models

alembic_cfg = Config("alembic.ini")
# Use sqlite in memory
alembic_cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")

# Generate the migration script
command.revision(alembic_cfg, autogenerate=True, message="Initial Phase 2 DB Schema")
print("Alembic generation complete.")
