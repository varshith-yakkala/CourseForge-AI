import os

MODELS_DIR = "backend/db/models"
os.makedirs(MODELS_DIR, exist_ok=True)

models = {
    "__init__.py": '''
from .user import User
from .course import Course
from .document import Document
from .lesson import Lesson
from .topic import Topic
from .subtopic import Subtopic
from .enrollment import CourseEnrollment
from .progress import UserProgress
from .quiz import Quiz
from .quiz_question import QuizQuestion
from .quiz_attempt import QuizAttempt
from .quiz_attempt_answer import QuizAttemptAnswer
from .flashcard import Flashcard
from .flashcard_review import FlashcardReview
from .chat_session import ChatSession
from .chat_message import ChatMessage
from .analytics_event import AnalyticsEvent
from .notification import Notification
from .bookmark import Bookmark
from .certificate import Certificate
''',

    "user.py": '''
import uuid
from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="student", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at = mapped_column(Text, nullable=True) # Will use DateTime

    # Relationships
    courses = relationship("Course", back_populates="owner")
''',

    "course.py": '''
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, Numeric, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Course(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "courses"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="processing", index=True, nullable=False)
    generation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags = mapped_column(ARRAY(Text), nullable=True, index=True)

    owner = relationship("User", back_populates="courses")
    document = relationship("Document", back_populates="course", uselist=False)
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
''',

    "document.py": '''
import uuid
from sqlalchemy import BigInteger, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Document(Base, UUIDMixin):
    __tablename__ = "documents"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), unique=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    insightforge_doc_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    index_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    indexed_at = mapped_column(DateTime(timezone=True), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    course = relationship("Course", back_populates="document")
''',

    "lesson.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Lesson(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "lessons"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    course = relationship("Course", back_populates="lessons")
    topics = relationship("Topic", back_populates="lesson", cascade="all, delete-orphan")
    quiz = relationship("Quiz", back_populates="lesson", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (Index("idx_lessons_course_order", "course_id", "order_index"),)
''',

    "topic.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Topic(Base, UUIDMixin):
    __tablename__ = "topics"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    key_terms = mapped_column(ARRAY(Text), nullable=True)
    created_at = mapped_column(Text)

    lesson = relationship("Lesson", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")
''',

    "subtopic.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class Subtopic(Base, UUIDMixin):
    __tablename__ = "subtopics"

    topic_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at = mapped_column(Text)

    topic = relationship("Topic", back_populates="subtopics")
''',

    "enrollment.py": '''
import uuid
from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class CourseEnrollment(Base, UUIDMixin):
    __tablename__ = "course_enrollments"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    enrolled_at = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    progress_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    last_accessed_at = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)
''',

    "progress.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class UserProgress(Base, UUIDMixin):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_progress_user_course", "user_id", "course_id"),)
''',

    "quiz.py": '''
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Quiz(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quizzes"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), unique=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    pass_score_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=70.0, nullable=False)
    time_limit_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lesson = relationship("Lesson", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
''',

    "quiz_question.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, ARRAY, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class QuizQuestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quiz_questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    options = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    source_chunk_ids = mapped_column(ARRAY(Text), nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
''',

    "quiz_attempt.py": '''
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class QuizAttempt(Base, UUIDMixin):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    started_at = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=True)
    score_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    time_taken_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)

    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("QuizAttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_quiz_attempts_user_quiz", "user_id", "quiz_id"),)
''',

    "quiz_attempt_answer.py": '''
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class QuizAttemptAnswer(Base, UUIDMixin):
    __tablename__ = "quiz_attempt_answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quiz_questions.id"))
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="answers")
''',

    "flashcard.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Flashcard(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "flashcards"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True, nullable=True)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    source_chunk_ids = mapped_column(ARRAY(Text), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)

    reviews = relationship("FlashcardReview", back_populates="flashcard", cascade="all, delete-orphan")
''',

    "flashcard_review.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Numeric, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class FlashcardReview(Base, UUIDMixin):
    __tablename__ = "flashcard_reviews"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    flashcard_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("flashcards.id", ondelete="CASCADE"))
    rating: Mapped[str] = mapped_column(String(10), nullable=False)
    next_review_at = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), default=2.5, nullable=False)
    reviewed_at = mapped_column(DateTime(timezone=True), nullable=False)

    flashcard = relationship("Flashcard", back_populates="reviews")

    __table_args__ = (Index("idx_flashcard_reviews_user_card", "user_id", "flashcard_id"),)
''',

    "chat_session.py": '''
import uuid
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_chat_sessions_user_course", "user_id", "course_id"),)
''',

    "chat_message.py": '''
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, Numeric, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class ChatMessage(Base, UUIDMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources = mapped_column(JSONB, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    generation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    session = relationship("ChatSession", back_populates="messages")
''',

    "analytics_event.py": '''
import uuid
from sqlalchemy import ForeignKey, String, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class AnalyticsEvent(Base, UUIDMixin):
    __tablename__ = "analytics_events"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    metadata_ = mapped_column("metadata", JSONB, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), index=True, nullable=False)
''',

    "notification.py": '''
import uuid
from sqlalchemy import Boolean, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Notification(Base, UUIDMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    link: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_ = mapped_column("metadata", JSONB, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)
''',

    "bookmark.py": '''
import uuid
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Bookmark(Base, UUIDMixin):
    __tablename__ = "bookmarks"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "entity_type", "entity_id"),
        Index("idx_bookmarks_user_course", "user_id", "course_id"),
    )
''',

    "certificate.py": '''
import uuid
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Certificate(Base, UUIDMixin):
    __tablename__ = "certificates"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    issued_at = mapped_column(DateTime(timezone=True), nullable=False)
    certificate_url: Mapped[str] = mapped_column(Text, nullable=False)
    verification_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)
'''
}

for filename, code in models.items():
    with open(os.path.join(MODELS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")

print("All models generated successfully.")
