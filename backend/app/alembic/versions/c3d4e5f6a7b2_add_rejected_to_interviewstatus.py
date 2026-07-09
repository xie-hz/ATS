"""Add REJECTED to interviewstatus enum

Revision ID: c3d4e5f6a7b2
Revises: b2c3d4e5f6a1
Create Date: 2026-07-10 10:00:00.000000
"""

from alembic import op

revision = "c3d4e5f6a7b2"
down_revision = "b2c3d4e5f6a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE interviewstatus ADD VALUE IF NOT EXISTS 'REJECTED'"
    )


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    pass
