"""
CourseForge AI — Export Service

Responsibility: Render course content to PDF and Markdown files.

Flow (Phase 3):
    - Load full course structure from DB
    - Render to HTML template
    - PDF: WeasyPrint HTML -> PDF
    - Markdown: Jinja2 markdown template
    - Save to exports/{user_id}/{course_id}/
    - Return download URL
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Course export to PDF and Markdown. Implemented in Phase 3."""

    def export_pdf(self, course_id: str, user_id: str) -> str:
        """
        Export course to PDF. Returns absolute file path.
        Implemented in Phase 3.
        """
        raise NotImplementedError("Implemented in Phase 3.")

    def export_markdown(self, course_id: str, user_id: str) -> str:
        """
        Export course to Markdown. Returns absolute file path.
        Implemented in Phase 3.
        """
        raise NotImplementedError("Implemented in Phase 3.")
