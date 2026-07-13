"""add meeting fields to interview

Revision ID: g6f7a8b9c0e1
Revises: f5e6a7b8c9d4
Create Date: 2026-07-12 16:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "g6f7a8b9c0e1"
down_revision = "f5e6a7b8c9d4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "interview",
        sa.Column("meeting_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "interview",
        sa.Column("meeting_no", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "interview",
        sa.Column("meeting_password", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("interview", "meeting_password")
    op.drop_column("interview", "meeting_no")
    op.drop_column("interview", "meeting_id")
