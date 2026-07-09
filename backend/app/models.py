import uuid
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class JobStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class ApplicationStage(StrEnum):
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    HIRED = "HIRED"
    REJECTED = "REJECTED"


class InterviewStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    REJECTED = "REJECTED"


class OfferStatus(StrEnum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class DataScopeType(StrEnum):
    ALL = "ALL"
    DEPARTMENT = "DEPARTMENT"
    SELF = "SELF"


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------


class DepartmentBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)


class Department(DepartmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    users: list[User] = Relationship(back_populates="department")
    jobs: list[Job] = Relationship(back_populates="department")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentPublic(DepartmentBase):
    id: uuid.UUID
    created_at: datetime | None = None


class DepartmentsPublic(SQLModel):
    data: list[DepartmentPublic]
    count: int


# ---------------------------------------------------------------------------
# Permission / Role (RBAC)
# ---------------------------------------------------------------------------


class Permission(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=64)
    description: str | None = Field(default=None, max_length=255)

    role_permissions: list[RolePermission] = Relationship(
        back_populates="permission",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class RoleBase(SQLModel):
    name: str = Field(min_length=1, max_length=64)
    code: str = Field(min_length=1, max_length=64)


class Role(RoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=64)

    user_roles: list[UserRole] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    role_permissions: list[RolePermission] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    data_scope: DataScope = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False}
    )


class RolePublic(RoleBase):
    id: uuid.UUID


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"

    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")
    role_id: uuid.UUID = Field(foreign_key="role.id", primary_key=True, ondelete="CASCADE")

    user: User = Relationship(back_populates="user_roles")
    role: Role = Relationship(back_populates="user_roles")


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permission"

    role_id: uuid.UUID = Field(foreign_key="role.id", primary_key=True, ondelete="CASCADE")
    permission_id: uuid.UUID = Field(
        foreign_key="permission.id", primary_key=True, ondelete="CASCADE"
    )

    role: Role = Relationship(back_populates="role_permissions")
    permission: Permission = Relationship(back_populates="role_permissions")


class DataScope(SQLModel, table=True):
    __tablename__ = "data_scope"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="role.id", unique=True, ondelete="CASCADE")
    scope_type: DataScopeType = Field(
        default=DataScopeType.SELF, sa_type=SAEnum(DataScopeType)
    )

    role: Role = Relationship(back_populates="data_scope")


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    name: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    department_id: uuid.UUID | None = None
    role_codes: list[str] = Field(default_factory=list)


class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None
    department_id: uuid.UUID | None = None
    role_codes: list[str] | None = None


class UserUpdateMe(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    department_id: uuid.UUID | None = Field(
        default=None, foreign_key="department.id", ondelete="SET NULL"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )

    department: Department | None = Relationship(back_populates="users")
    user_roles: list[UserRole] = Relationship(back_populates="user")


class UserPublic(UserBase):
    id: uuid.UUID
    department_id: uuid.UUID | None = None
    roles: list[str] = Field(default_factory=list)
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------


class JobBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    department_id: uuid.UUID | None = Field(default=None, foreign_key="department.id")
    headcount: int = Field(default=1, ge=1)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = None
    requirements: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    department_id: uuid.UUID | None = None
    headcount: int | None = Field(default=None, ge=1)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=255)
    description: str | None = None
    requirements: str | None = None


class Job(JobBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: JobStatus = Field(default=JobStatus.DRAFT, sa_type=SAEnum(JobStatus))
    creator_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )

    department: Department | None = Relationship(back_populates="jobs")
    applications: list[Application] = Relationship(
        back_populates="job",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class JobPublic(JobBase):
    id: uuid.UUID
    status: JobStatus
    creator_id: uuid.UUID | None = None
    created_at: datetime | None = None


class JobsPublic(SQLModel):
    data: list[JobPublic]
    count: int


# ---------------------------------------------------------------------------
# Candidate
# ---------------------------------------------------------------------------


class CandidateBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    source: str | None = Field(default=None, max_length=64)


class CandidateCreate(CandidateBase):
    tags: list[str] = Field(default_factory=list)
    resume_url: str | None = None


class CandidateUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    source: str | None = Field(default=None, max_length=64)
    tags: list[str] | None = None
    resume_url: str | None = None


class Candidate(CandidateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tags: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB, nullable=False, default=list)
    )
    resume_url: str | None = Field(default=None, max_length=512)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )

    applications: list[Application] = Relationship(
        back_populates="candidate",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class CandidatePublic(CandidateBase):
    id: uuid.UUID
    tags: list[str] = Field(default_factory=list)
    resume_url: str | None = None
    created_at: datetime | None = None


class CandidatesPublic(SQLModel):
    data: list[CandidatePublic]
    count: int


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


class ApplicationCreate(SQLModel):
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    source: str | None = Field(default=None, max_length=64)


class Application(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    candidate_id: uuid.UUID = Field(foreign_key="candidate.id", ondelete="CASCADE")
    job_id: uuid.UUID = Field(foreign_key="job.id", ondelete="CASCADE")
    stage: ApplicationStage = Field(
        default=ApplicationStage.APPLIED, sa_type=SAEnum(ApplicationStage)
    )
    source: str | None = Field(default=None, max_length=64)
    owner_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )

    candidate: Candidate = Relationship(back_populates="applications")
    job: Job = Relationship(back_populates="applications")
    interviews: list[Interview] = Relationship(
        back_populates="application",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    offer: Offer = Relationship(
        back_populates="application",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )


class ApplicationPublic(SQLModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    stage: ApplicationStage
    source: str | None = None
    owner_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApplicationsPublic(SQLModel):
    data: list[ApplicationPublic]
    count: int


class ApplicationTransition(SQLModel):
    target_stage: ApplicationStage


class BatchAdvance(SQLModel):
    application_ids: list[uuid.UUID]
    target_stage: ApplicationStage


# ---------------------------------------------------------------------------
# Interview
# ---------------------------------------------------------------------------


class InterviewCreate(SQLModel):
    application_id: uuid.UUID
    interviewer_id: uuid.UUID
    round: int = Field(default=1, ge=1)
    scheduled_time: datetime


class InterviewUpdate(SQLModel):
    interviewer_id: uuid.UUID | None = None
    round: int | None = Field(default=None, ge=1)
    scheduled_time: datetime | None = None


class Interview(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    application_id: uuid.UUID = Field(
        foreign_key="application.id", ondelete="CASCADE"
    )
    interviewer_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    round: int = Field(default=1, ge=1)
    scheduled_time: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
    status: InterviewStatus = Field(
        default=InterviewStatus.SCHEDULED, sa_type=SAEnum(InterviewStatus)
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    application: Application = Relationship(back_populates="interviews")
    feedback: InterviewFeedback = Relationship(
        back_populates="interview",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )


class InterviewPublic(SQLModel):
    id: uuid.UUID
    application_id: uuid.UUID
    interviewer_id: uuid.UUID | None = None
    round: int
    scheduled_time: datetime
    status: InterviewStatus
    created_at: datetime | None = None


class InterviewsPublic(SQLModel):
    data: list[InterviewPublic]
    count: int


# ---------------------------------------------------------------------------
# InterviewFeedback
# ---------------------------------------------------------------------------


class FeedbackCreate(SQLModel):
    score: int = Field(ge=0, le=100)
    recommend: bool
    comment: str | None = Field(default=None, max_length=2000)


class InterviewFeedback(SQLModel, table=True):
    __tablename__ = "interview_feedback"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    interview_id: uuid.UUID = Field(
        foreign_key="interview.id", unique=True, ondelete="CASCADE"
    )
    score: int = Field(ge=0, le=100)
    recommend: bool
    comment: str | None = Field(default=None, max_length=2000)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    interview: Interview = Relationship(back_populates="feedback")


class FeedbackPublic(SQLModel):
    id: uuid.UUID
    interview_id: uuid.UUID
    score: int
    recommend: bool
    comment: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Offer
# ---------------------------------------------------------------------------


class OfferCreate(SQLModel):
    application_id: uuid.UUID
    salary: int = Field(ge=0)


class OfferUpdate(SQLModel):
    salary: int = Field(ge=0)


class Offer(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    application_id: uuid.UUID = Field(
        foreign_key="application.id", unique=True, ondelete="CASCADE"
    )
    salary: int = Field(ge=0)
    status: OfferStatus = Field(default=OfferStatus.DRAFT, sa_type=SAEnum(OfferStatus))
    creator_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    approved_by: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": get_datetime_utc},
    )

    application: Application = Relationship(back_populates="offer")


class OfferPublic(SQLModel):
    id: uuid.UUID
    application_id: uuid.UUID
    salary: int
    status: OfferStatus
    creator_id: uuid.UUID | None = None
    approved_by: uuid.UUID | None = None
    created_at: datetime | None = None


class OffersPublic(SQLModel):
    data: list[OfferPublic]
    count: int


# ---------------------------------------------------------------------------
# Candidate portal auth
# ---------------------------------------------------------------------------


class EmailVerificationCode(SQLModel, table=True):
    __tablename__ = "email_verification_code"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(index=True, max_length=255)
    code: str = Field(max_length=16)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))  # type: ignore
    used: bool = Field(default=False)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class SendCodeRequest(SQLModel):
    email: EmailStr


class VerifyCodeRequest(SQLModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=16)


class PortalApplicationSubmit(SQLModel):
    job_id: uuid.UUID
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    resume_url: str | None = Field(default=None, max_length=512)
    source: str | None = Field(default=None, max_length=64)


class PortalApplicationPublic(SQLModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    stage: ApplicationStage
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------


class NotificationBase(SQLModel):
    type: str = Field(max_length=64)
    content: str = Field(max_length=500)


class Notification(NotificationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    read_status: bool = Field(default=False)
    related_type: str | None = Field(default=None, max_length=64)
    related_id: uuid.UUID | None = Field(default=None)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class NotificationPublic(NotificationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    read_status: bool
    related_type: str | None = None
    related_id: uuid.UUID | None = None
    created_at: datetime | None = None


class NotificationsPublic(SQLModel):
    data: list[NotificationPublic]
    count: int


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", ondelete="SET NULL"
    )
    action: str = Field(max_length=64)
    resource_type: str = Field(max_length=64)
    resource_id: uuid.UUID | None = Field(default=None)
    before_data: dict | None = Field(default=None, sa_column=Column(JSONB))
    after_data: dict | None = Field(default=None, sa_column=Column(JSONB))
    ip: str | None = Field(default=None, max_length=64)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class AuditLogPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None = None
    before_data: dict | None = None
    after_data: dict | None = None
    ip: str | None = None
    created_at: datetime | None = None


class AuditLogsPublic(SQLModel):
    data: list[AuditLogPublic]
    count: int


class AnalyticsSummary(SQLModel):
    total_jobs: int = 0
    open_jobs: int = 0
    total_candidates: int = 0
    total_applications: int = 0
    funnel: dict = Field(default_factory=dict)
    channels: dict = Field(default_factory=dict)
    hired: int = 0
    conversion_rate: float = 0


# ---------------------------------------------------------------------------
# Auth / generic
# ---------------------------------------------------------------------------


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PortalToken(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None


class RefreshTokenRequest(SQLModel):
    refresh_token: str
