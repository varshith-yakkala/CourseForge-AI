"""Initial database schema migration creating all ORM tables.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-07-22
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.Text()),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login_at', sa.Text()),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'courses',
        sa.Column('owner_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('thumbnail_url', sa.Text()),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('generation_error', sa.Text()),
        sa.Column('difficulty', sa.String(length=20)),
        sa.Column('estimated_duration_min', sa.Integer()),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.Text())),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'notifications',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text()),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('link', sa.Text()),
        sa.Column('metadata', postgresql.JSONB(astext_type=Text())),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'user_achievements',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('badge_key', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon_name', sa.String(length=50), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'analytics_events',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID()),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=Text())),
        sa.Column('session_id', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
    )
    op.create_table(
        'bookmarks',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', sa.Uuid(), nullable=False),
        sa.Column('note', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'entity_type', 'entity_id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'certificates',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('certificate_url', sa.Text(), nullable=False),
        sa.Column('verification_code', sa.String(length=64), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.UniqueConstraint('user_id', 'course_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'chat_sessions',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500)),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'course_enrollments',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('progress_pct', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True)),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.UniqueConstraint('user_id', 'course_id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'documents',
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('owner_id', postgresql.UUID(), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=False),
        sa.Column('stored_path', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('page_count', sa.Integer()),
        sa.Column('insightforge_doc_id', sa.String(length=255)),
        sa.Column('index_status', sa.String(length=30), nullable=False),
        sa.Column('chunk_count', sa.Integer()),
        sa.Column('indexed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.UniqueConstraint('course_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'lessons',
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('summary', sa.Text()),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('estimated_duration_min', sa.Integer()),
        sa.Column('content_markdown', sa.Text()),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True)),
        sa.Column('generation_error', sa.Text()),
        sa.Column('llm_metadata', sa.Text()),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'study_plans',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('daily_goal_min', sa.Integer(), nullable=False),
        sa.Column('weekly_goal_min', sa.Integer(), nullable=False),
        sa.Column('target_completion_date', sa.Date()),
        sa.Column('preferred_study_days', postgresql.ARRAY(sa.String())),
        sa.Column('preferred_study_time', sa.String(length=50)),
        sa.Column('difficulty_pref', sa.String(length=20), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'weekly_reports',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('week_start_date', sa.Date(), nullable=False),
        sa.Column('summary_md', sa.Text(), nullable=False),
        sa.Column('metrics_json', postgresql.JSONB(astext_type=Text())),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'chat_messages',
        sa.Column('session_id', postgresql.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSONB(astext_type=Text())),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3)),
        sa.Column('generation_time_ms', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'flashcards',
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('lesson_id', postgresql.UUID()),
        sa.Column('front', sa.Text(), nullable=False),
        sa.Column('back', sa.Text(), nullable=False),
        sa.Column('source_chunk_ids', postgresql.ARRAY(sa.Text())),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'quizzes',
        sa.Column('lesson_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('pass_score_pct', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('time_limit_min', sa.Integer()),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('shuffle_questions', sa.Boolean(), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.UniqueConstraint('lesson_id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'topics',
        sa.Column('lesson_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('key_terms', postgresql.ARRAY(sa.Text())),
        sa.Column('created_at', sa.Text()),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'flashcard_reviews',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('flashcard_id', postgresql.UUID(), nullable=False),
        sa.Column('rating', sa.String(length=10), nullable=False),
        sa.Column('next_review_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('interval_days', sa.Integer(), nullable=False),
        sa.Column('ease_factor', sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['flashcard_id'], ['flashcards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'quiz_attempts',
        sa.Column('quiz_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(timezone=True)),
        sa.Column('score_pct', sa.Numeric(precision=5, scale=2)),
        sa.Column('passed', sa.Boolean()),
        sa.Column('time_taken_sec', sa.Integer()),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'quiz_questions',
        sa.Column('quiz_id', postgresql.UUID(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(length=20), nullable=False),
        sa.Column('options', postgresql.JSONB(astext_type=Text())),
        sa.Column('correct_answer', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text()),
        sa.Column('difficulty', sa.String(length=20)),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('source_chunk_ids', postgresql.ARRAY(sa.Text())),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'subtopics',
        sa.Column('topic_id', postgresql.UUID(), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.Text()),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id']),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
    )
    op.create_table(
        'user_progress',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('course_id', postgresql.UUID(), nullable=False),
        sa.Column('lesson_id', postgresql.UUID()),
        sa.Column('topic_id', postgresql.UUID()),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('completion_percentage', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('last_opened_at', sa.DateTime(timezone=True)),
        sa.Column('last_scroll_position', sa.Integer()),
        sa.Column('time_spent_sec', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_table(
        'quiz_attempt_answers',
        sa.Column('attempt_id', postgresql.UUID(), nullable=False),
        sa.Column('question_id', postgresql.UUID(), nullable=False),
        sa.Column('user_answer', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('time_spent_sec', sa.Integer()),
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['quiz_questions.id']),
        sa.ForeignKeyConstraint(['attempt_id'], ['quiz_attempts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table('quiz_attempt_answers')
    op.drop_table('user_progress')
    op.drop_table('subtopics')
    op.drop_table('quiz_questions')
    op.drop_table('quiz_attempts')
    op.drop_table('flashcard_reviews')
    op.drop_table('topics')
    op.drop_table('quizzes')
    op.drop_table('flashcards')
    op.drop_table('chat_messages')
    op.drop_table('weekly_reports')
    op.drop_table('study_plans')
    op.drop_table('lessons')
    op.drop_table('documents')
    op.drop_table('course_enrollments')
    op.drop_table('chat_sessions')
    op.drop_table('certificates')
    op.drop_table('bookmarks')
    op.drop_table('analytics_events')
    op.drop_table('user_achievements')
    op.drop_table('notifications')
    op.drop_table('courses')
    op.drop_table('users')
