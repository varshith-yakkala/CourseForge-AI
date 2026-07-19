"""
CourseForge AI — Flashcard Service
Responsibility: Generate flashcard decks, support multiple study modes, and compute SuperMemo SM-2 spaced repetition intervals.
"""
from __future__ import annotations

import json
import random
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.flashcard import Flashcard
from db.models.flashcard_review import FlashcardReview
from db.models.lesson import Lesson
from db.models.document import Document
from llm.prompt_manager import PromptManager
from llm.schemas import FlashcardGenerationResponse
from insightforge.engine import InsightForgeEngine
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)


class FlashcardService:
    """Service to handle AI flashcard generation, modes, and SM-2 spaced repetition."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()

    async def get_or_generate_deck(
        self, course_id: str, lesson_id: str | None = None, force: bool = False
    ) -> list[Flashcard]:
        """
        Fetch or on-demand generate flashcards for a course or specific lesson.
        """
        stmt = select(Flashcard).where(Flashcard.course_id == course_id)
        if lesson_id:
            stmt = stmt.where(Flashcard.lesson_id == lesson_id)
        stmt = stmt.order_by(Flashcard.order_index)

        res = await self.db.execute(stmt)
        cards = res.scalars().all()

        if cards and not force:
            return cards

        # Fetch Lesson context if specified
        lesson_title = "Course Flashcards"
        lesson_markdown = ""
        if lesson_id:
            stmt_l = select(Lesson).where(Lesson.id == lesson_id)
            res_l = await self.db.execute(stmt_l)
            lesson = res_l.scalar_one_or_none()
            if lesson:
                lesson_title = lesson.title
                lesson_markdown = lesson.content_markdown or lesson.summary or lesson.title

        stmt_doc = select(Document).where(Document.course_id == course_id)
        res_doc = await self.db.execute(stmt_doc)
        document = res_doc.scalar_one_or_none()

        document_context = ""
        if document and document.index_status == "ready" and document.insightforge_doc_id:
            try:
                chunks = self.engine.retrieve_chunks(
                    query=f"{lesson_title} key terms flashcards concepts",
                    doc_ids=[document.insightforge_doc_id],
                    top_k=6,
                )
                document_context = "\n\n".join([c.content for c in chunks])
            except Exception as e:
                logger.warning(f"Could not fetch chunks for flashcard generation: {e}")

        # Build prompt
        schema_json = FlashcardGenerationResponse.model_json_schema()
        prompt = PromptManager.build(
            "flashcard_generation",
            version="v1",
            lesson_title=lesson_title,
            lesson_markdown=lesson_markdown or "General course topic context.",
            document_context=document_context or "General course document context.",
            schema=json.dumps(schema_json, indent=2),
        )

        query_res = self.engine.query(
            question=f"Generate flashcard deck for {lesson_title}",
            doc_ids=[document.insightforge_doc_id] if (document and document.insightforge_doc_id) else [],
            prompt_override=prompt,
        )

        answer = query_res.answer
        if not answer:
            raise CourseForgeError("LLM failed to generate flashcard response", status_code=500)

        try:
            cleaned = answer.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            
            data = json.loads(cleaned.strip())
            fc_resp = FlashcardGenerationResponse(**data)
        except Exception as exc:
            logger.error(f"Failed to parse flashcard response: {answer}")
            raise CourseForgeError(f"Flashcard parsing error: {exc}", status_code=500)

        created_cards = []
        for idx, item in enumerate(fc_resp.flashcards):
            card = Flashcard(
                course_id=course_id,
                lesson_id=lesson_id,
                front=item.front,
                back=item.back,
                order_index=idx,
            )
            self.db.add(card)
            created_cards.append(card)

        await self.db.commit()
        return created_cards

    async def get_mode_deck(
        self, course_id: str, mode: str = "all", user_id: str | None = None
    ) -> list[Flashcard]:
        """
        Filter deck by Mode: 'all', 'shuffle', 'due_today', 'weak_topics', 'mastered'.
        """
        stmt = select(Flashcard).where(Flashcard.course_id == course_id)
        res = await self.db.execute(stmt)
        cards = res.scalars().all()

        if not cards:
            return []

        if mode == "shuffle":
            shuffled = list(cards)
            random.shuffle(shuffled)
            return shuffled

        if mode == "due_today" and user_id:
            now = datetime.now(timezone.utc)
            # Find cards with next_review_at <= now or no review yet
            due_cards = []
            for card in cards:
                stmt_rev = select(FlashcardReview).where(
                    FlashcardReview.user_id == user_id,
                    FlashcardReview.flashcard_id == card.id,
                ).order_by(FlashcardReview.reviewed_at.desc())
                res_rev = await self.db.execute(stmt_rev)
                last_rev = res_rev.scalar_one_or_none()

                if not last_rev or last_rev.next_review_at <= now:
                    due_cards.append(card)
            return due_cards if due_cards else cards

        return cards

    async def review_flashcard(
        self, user_id: str, flashcard_id: str, rating_key: str
    ) -> FlashcardReview:
        """
        SuperMemo SM-2 Spaced Repetition Algorithm implementation.
        rating_key: 'again' (q=1), 'hard' (q=3), 'good' (q=4), 'easy' (q=5)
        """
        q_map = {"again": 1, "hard": 3, "good": 4, "easy": 5}
        q = q_map.get(rating_key.lower(), 4)

        # Get last review if exists
        stmt_last = select(FlashcardReview).where(
            FlashcardReview.user_id == user_id,
            FlashcardReview.flashcard_id == flashcard_id,
        ).order_by(FlashcardReview.reviewed_at.desc())
        res_last = await self.db.execute(stmt_last)
        last_rev = res_last.scalar_one_or_none()

        old_ease = float(last_rev.ease_factor) if last_rev else 2.5
        old_interval = last_rev.interval_days if last_rev else 1

        # Calculate new ease factor: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        new_ease = max(1.3, old_ease + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))

        if q < 3:
            # Failed review -> Reset interval
            new_interval = 1
        else:
            if not last_rev:
                new_interval = 1
            elif old_interval == 1:
                new_interval = 6
            else:
                new_interval = int(round(old_interval * new_ease))

        now = datetime.now(timezone.utc)
        next_review_at = now + timedelta(days=new_interval)

        review = FlashcardReview(
            user_id=user_id,
            flashcard_id=flashcard_id,
            rating=rating_key,
            interval_days=new_interval,
            ease_factor=round(new_ease, 2),
            next_review_at=next_review_at,
            reviewed_at=now,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review
