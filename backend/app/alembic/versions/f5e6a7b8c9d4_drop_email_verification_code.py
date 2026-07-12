"""Drop email_verification_code table (codes now in Redis)

Revision ID: f5e6a7b8c9d4
Revises: e4d5f6a7b8c3
Create Date: 2026-07-10 12:00:00.000000
"""

from alembic import op

revision = "f5e6a7b8c9d4"
down_revision = "e4d5f6a7b8c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verification codes moved to Redis (TTL + delete-on-use); the table is
    # no longer written or read.
    op.execute("DROP TABLE IF EXISTS email_verification_code")


def downgrade() -> None:
    # Recreate a minimal table for reversibility.
    import sqlalchemy as sa

    op.create_table(
        "email_verification_code",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("code", sa.String(16), nullable=False),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
