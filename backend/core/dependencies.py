"""
CourseForge AI — Core Dependencies Compatibility Module

Re-exports FastAPI dependencies from api.deps for backward compatibility.
"""

from api.deps import get_current_active_user, get_current_user, get_db

__all__ = ["get_current_user", "get_current_active_user", "get_db"]
