"""Add is_shared and share_token to courses, quality_rating to flashcard_reviews, and new feature tables.

Revision ID: 003
Revises: 002
Create Date: 2026-07-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    tables = inspector.get_table_names()
    return table_name in tables


def upgrade() -> None:
    # 1. Add missing columns to courses table
    if not column_exists('courses', 'is_shared'):
        op.add_column('courses', sa.Column('is_shared', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    if not column_exists('courses', 'share_token'):
        op.add_column('courses', sa.Column('share_token', sa.String(length=64), nullable=True))
        op.create_unique_constraint('uq_courses_share_token', 'courses', ['share_token'])

    # 2. Add missing columns to flashcard_reviews table
    if not column_exists('flashcard_reviews', 'quality_rating'):
        op.add_column('flashcard_reviews', sa.Column('quality_rating', sa.Integer(), nullable=True, server_default=sa.text('0')))
    if not column_exists('flashcard_reviews', 'repetition_number'):
        op.add_column('flashcard_reviews', sa.Column('repetition_number', sa.Integer(), nullable=True, server_default=sa.text('0')))

    # 3. Create notes table if missing
    if not table_exists('notes'):
        op.create_table(
            'notes',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('course_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('lesson_id', sa.UUID(as_uuid=True), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('highlight_color', sa.String(length=20), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )

    # 4. Create study_sessions table if missing
    if not table_exists('study_sessions'):
        op.create_table(
            'study_sessions',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('course_id', sa.UUID(as_uuid=True), nullable=True),
            sa.Column('duration_minutes', sa.Integer(), nullable=False),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )

    # 5. Create topic_masteries table if missing
    if not table_exists('topic_masteries'):
        op.create_table(
            'topic_masteries',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('topic_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('mastery_score', sa.Float(), nullable=False, server_default=sa.text('0.0')),
            sa.Column('attempts_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
            sa.Column('last_practiced_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 6. Create workspace_artifacts table if missing
    if not table_exists('workspace_artifacts'):
        op.create_table(
            'workspace_artifacts',
            sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('course_id', sa.UUID(as_uuid=True), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('artifact_type', sa.String(length=50), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('version', sa.Integer(), nullable=False, server_default=sa.text('1')),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('workspace_artifacts')
    op.drop_table('topic_masteries')
    op.drop_table('study_sessions')
    op.drop_table('notes')

    op.drop_column('flashcard_reviews', 'repetition_number')
    op.drop_column('flashcard_reviews', 'quality_rating')

    op.drop_constraint('uq_courses_share_token', 'courses', type_='unique')
    op.drop_column('courses', 'share_token')
    op.drop_column('courses', 'is_shared')
