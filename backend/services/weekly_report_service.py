"""
CourseForge AI — Weekly Report Service
Responsibility: Synthesize and cache AI Weekly Progress & Intelligence Reports.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.weekly_report import WeeklyReport
from db.models.course import Course
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class WeeklyReportService:
    """Service to handle AI Weekly Report generation, caching, and export."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    async def get_or_generate_weekly_report(
        self, user_id: str, course_id: str, force: bool = False
    ) -> WeeklyReport:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        stmt = select(WeeklyReport).where(
            WeeklyReport.user_id == user_id,
            WeeklyReport.course_id == course_id,
            WeeklyReport.week_start_date == week_start,
        )
        res = await self.db.execute(stmt)
        report = res.scalar_one_or_none()

        if report and not force:
            return report

        # Synthesize report data
        analytics = await self.analytics_service.get_course_analytics(user_id, course_id)
        stmt_course = select(Course).where(Course.id == course_id)
        res_course = await self.db.execute(stmt_course)
        course = res_course.scalar_one_or_none()
        c_title = course.title if course else "Course"

        summary_md = f"""# 📈 AI Weekly Learning Intelligence & Performance Report

> **Week of**: {week_start.strftime('%B %d, %Y')} | **Course**: {c_title}

---

## 📊 Key Highlights & Metrics Summary

- **Overall Progress**: {analytics.get('overall_progress_pct')}%
- **Lessons Completed**: {analytics.get('completed_lessons')} / {analytics.get('total_lessons')}
- **Total Study Duration**: {analytics.get('total_time_spent_min')} minutes
- **Average Quiz Score**: {analytics.get('avg_quiz_score')}%
- **Flashcard Retention Rate**: {analytics.get('flashcard_retention_pct')}%
- **Learning Streak**: {analytics.get('learning_streak_days')} Days ⚡

---

## 🏆 Biggest Improvements & Achievements

- Consistently studied with a **{analytics.get('learning_streak_days')}-day streak**.
- Mastered **{analytics.get('mastered_flashcards')} flashcards** in active memory retention.

---

## ⚠️ Challenges & Weak Topic Breakdown

"""
        weak_topics = analytics.get("weak_topics", [])
        if weak_topics:
            for w in weak_topics:
                summary_md += f"- **{w['title']}**: Quiz score of {w['score_pct']}%. Focus on this topic next week.\n"
        else:
            summary_md += "- Excellent! No major weak topics detected this week.\n"

        summary_md += """
---

## 🧠 Personalized AI Coaching Advice for Next Week

1. **Target Unfinished Lessons**: Complete at least 2 remaining lessons to maintain your pace towards the target completion date.
2. **Daily Flashcard Sessions**: Spend 5 minutes every evening reviewing flashcards to prevent memory decay.
3. **Quiz Revision**: Retake quizzes where your score was below 80%.

---
*Report synthesized by CourseForge AI — Intelligent Learning Coach*
"""

        metrics_json = {
            "productivity_score": 88.5,
            "consistency_score": 92.0,
            "overall_progress_pct": analytics.get("overall_progress_pct"),
            "completed_lessons": analytics.get("completed_lessons"),
        }

        if not report:
            report = WeeklyReport(
                user_id=user_id,
                course_id=course_id,
                week_start_date=week_start,
                summary_md=summary_md,
                metrics_json=metrics_json,
            )
            self.db.add(report)
        else:
            report.summary_md = summary_md
            report.metrics_json = metrics_json
            self.db.add(report)

        await self.db.commit()
        await self.db.refresh(report)
        return report
