"""Fix Text timestamps to DateTime

Revision ID: 002
Revises: 001
Create Date: 2026-07-22 17:43:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. topics.created_at
    op.execute("ALTER TABLE topics ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at::timestamp with time zone")
    op.execute("ALTER TABLE topics ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE topics ALTER COLUMN created_at SET NOT NULL")
    
    # 2. subtopics.created_at
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE USING created_at::timestamp with time zone")
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at SET NOT NULL")
    
    # 3. users.last_login_at
    op.execute("ALTER TABLE users ALTER COLUMN last_login_at TYPE TIMESTAMP WITH TIME ZONE USING last_login_at::timestamp with time zone")

    # 4. topics.updated_at (added by TimestampMixin)
    op.add_column('topics', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    
    # 5. subtopics.updated_at (added by TimestampMixin)
    op.add_column('subtopics', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    # Revert topics.updated_at
    op.drop_column('topics', 'updated_at')
    
    # Revert subtopics.updated_at
    op.drop_column('subtopics', 'updated_at')

    # Revert topics.created_at
    op.execute("ALTER TABLE topics ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE topics ALTER COLUMN created_at TYPE TEXT USING created_at::text")
    op.execute("ALTER TABLE topics ALTER COLUMN created_at DROP NOT NULL")
    
    # Revert subtopics.created_at
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at TYPE TEXT USING created_at::text")
    op.execute("ALTER TABLE subtopics ALTER COLUMN created_at DROP NOT NULL")
    
    # Revert users.last_login_at
    op.execute("ALTER TABLE users ALTER COLUMN last_login_at TYPE TEXT USING last_login_at::text")
