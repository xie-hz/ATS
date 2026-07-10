"""Add pg_trgm GIN indexes for candidate/job search

Phase-1 PostgreSQL-native search (design doc §14). We use pg_trgm trigram
indexes rather than tsvector because candidate names are often CJK, where
tsvector tokenization cannot do substring matches. pg_trgm accelerates the
existing ILIKE substring queries (name / email / job title) and handles CJK.

Revision ID: e4d5f6a7b8c3
Revises: c3d4e5f6a7b2
Create Date: 2026-07-10 11:00:00.000000
"""

from alembic import op

revision = "e4d5f6a7b8c3"
down_revision = "c3d4e5f6a7b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_candidate_name_trgm "
        "ON candidate USING gin (name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_candidate_email_trgm "
        "ON candidate USING gin (email gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_job_title_trgm "
        "ON job USING gin (title gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_job_title_trgm")
    op.execute("DROP INDEX IF EXISTS ix_candidate_email_trgm")
    op.execute("DROP INDEX IF EXISTS ix_candidate_name_trgm")
    # Leave pg_trgm extension installed; other future indexes may depend on it.
