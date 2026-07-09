"""ATS initial schema: RBAC + recruitment domain tables

Revision ID: a1b2c3d4e5f6
Revises: fe56fa70289e
Create Date: 2026-07-08 12:00:00.000000

Drops the template `item` table, alters `user` for RBAC (drops
is_superuser/full_name, adds name/department_id/updated_at), and creates the
ATS tables: department, role, permission, user_role, role_permission,
data_scope, job, candidate, application, interview, interview_feedback,
offer, email_verification_code.
"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

from app.models import (
    ApplicationStage,
    DataScopeType,
    InterviewStatus,
    JobStatus,
    OfferStatus,
)

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop the old template item table.
    op.drop_table("item")

    # 2. Department (created before user FK).
    op.create_table(
        "department",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 3. Alter user table for RBAC.
    op.drop_column("user", "is_superuser")
    op.drop_column("user", "full_name")
    op.add_column("user", sa.Column("name", sa.String(length=100), nullable=True))
    op.add_column(
        "user",
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "user_department_id_fkey",
        "user",
        "department",
        ["department_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 4. RBAC tables.
    op.create_table(
        "role",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_role_code", "role", ["code"], unique=True)

    op.create_table(
        "permission",
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_permission_code", "permission", ["code"], unique=True)

    op.create_table(
        "user_role",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["role.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "role_permission",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "permission_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["role.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permission.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "data_scope",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "scope_type", sa.Enum(DataScopeType), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["role.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id"),
    )

    # 5. Recruitment domain tables.
    op.create_table(
        "job",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column(
            "department_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("headcount", sa.Integer(), nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column(
            "requirements", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Enum(JobStatus), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["department.id"]),
        sa.ForeignKeyConstraint(
            ["creator_id"], ["user.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "candidate",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("resume_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidate_email", "candidate", ["email"], unique=False)

    op.create_table(
        "application",
        sa.Column(
            "candidate_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.Enum(ApplicationStage), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["candidate_id"], ["candidate.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["job.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "interview",
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "interviewer_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column(
            "scheduled_time", sa.DateTime(timezone=True), nullable=False
        ),
        sa.Column("status", sa.Enum(InterviewStatus), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"], ["application.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["interviewer_id"], ["user.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "interview_feedback",
        sa.Column(
            "interview_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("recommend", sa.Boolean(), nullable=False),
        sa.Column(
            "comment", sa.String(length=2000), nullable=True
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["interview_id"], ["interview.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("interview_id"),
    )

    op.create_table(
        "offer",
        sa.Column(
            "application_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("salary", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum(OfferStatus), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "approved_by", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["application_id"], ["application.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["creator_id"], ["user.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["user.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("application_id"),
    )

    # 6. Candidate portal email-code auth.
    op.create_table(
        "email_verification_code",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_email_verification_code_email",
        "email_verification_code",
        ["email"],
        unique=False,
    )


def downgrade() -> None:
    # Reverse is best-effort: drop ATS tables and restore the user columns.
    # The template `item` table is not recreated.
    op.drop_index(
        "ix_email_verification_code_email", table_name="email_verification_code"
    )
    op.drop_table("email_verification_code")

    op.drop_table("offer")
    op.drop_table("interview_feedback")
    op.drop_table("interview")
    op.drop_table("application")
    op.drop_index("ix_candidate_email", table_name="candidate")
    op.drop_table("candidate")
    op.drop_table("job")

    op.drop_table("data_scope")
    op.drop_table("role_permission")
    op.drop_table("user_role")
    op.drop_index("ix_permission_code", table_name="permission")
    op.drop_table("permission")
    op.drop_index("ix_role_code", table_name="role")
    op.drop_table("role")

    op.drop_constraint("user_department_id_fkey", "user", type_="foreignkey")
    op.drop_column("user", "updated_at")
    op.drop_column("user", "department_id")
    op.drop_column("user", "name")
    op.add_column(
        "user",
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.add_column("user", sa.Column("is_superuser", sa.Boolean(), nullable=False))
    op.drop_table("department")
