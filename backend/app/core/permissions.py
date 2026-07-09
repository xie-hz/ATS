"""RBAC permission constants, role definitions, and permission queries.

Role -> Permission and Role -> DataScope mappings live here so that
`init_db` can seed them and `deps.require_permission` can enforce them.
"""

from sqlmodel import Session, select

from app.models import (
    DataScope,
    DataScopeType,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)


class Permissions:
    # Job
    JOB_CREATE = "job:create"
    JOB_READ = "job:read"
    JOB_PUBLISH = "job:publish"
    JOB_CLOSE = "job:close"
    # Candidate
    CANDIDATE_READ = "candidate:read"
    CANDIDATE_CREATE = "candidate:create"
    CANDIDATE_UPDATE = "candidate:update"
    # Application
    APPLICATION_READ = "application:read"
    APPLICATION_ADVANCE = "application:advance"
    APPLICATION_REJECT = "application:reject"
    APPLICATION_RESTORE = "application:restore"
    # Interview
    INTERVIEW_CREATE = "interview:create"
    INTERVIEW_READ = "interview:read"
    # Feedback
    FEEDBACK_CREATE = "feedback:create"
    # Offer
    OFFER_READ = "offer:read"
    OFFER_CREATE = "offer:create"
    OFFER_SUBMIT = "offer:submit"
    OFFER_APPROVE = "offer:approve"
    OFFER_SEND = "offer:send"
    # User management
    USER_MANAGE = "user:manage"


class Roles:
    ADMIN = "admin"
    HR = "hr"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"


ALL_PERMISSIONS: list[str] = [
    Permissions.JOB_CREATE,
    Permissions.JOB_READ,
    Permissions.JOB_PUBLISH,
    Permissions.JOB_CLOSE,
    Permissions.CANDIDATE_READ,
    Permissions.CANDIDATE_CREATE,
    Permissions.CANDIDATE_UPDATE,
    Permissions.APPLICATION_READ,
    Permissions.APPLICATION_ADVANCE,
    Permissions.APPLICATION_REJECT,
    Permissions.APPLICATION_RESTORE,
    Permissions.INTERVIEW_CREATE,
    Permissions.INTERVIEW_READ,
    Permissions.FEEDBACK_CREATE,
    Permissions.OFFER_READ,
    Permissions.OFFER_CREATE,
    Permissions.OFFER_SUBMIT,
    Permissions.OFFER_APPROVE,
    Permissions.OFFER_SEND,
    Permissions.USER_MANAGE,
]


ROLE_PERMISSIONS: dict[str, list[str]] = {
    Roles.ADMIN: list(ALL_PERMISSIONS),
    Roles.HR: [
        Permissions.JOB_CREATE,
        Permissions.JOB_READ,
        Permissions.JOB_PUBLISH,
        Permissions.JOB_CLOSE,
        Permissions.CANDIDATE_READ,
        Permissions.CANDIDATE_CREATE,
        Permissions.CANDIDATE_UPDATE,
        Permissions.APPLICATION_READ,
        Permissions.APPLICATION_ADVANCE,
        Permissions.APPLICATION_REJECT,
        Permissions.APPLICATION_RESTORE,
        Permissions.INTERVIEW_CREATE,
        Permissions.INTERVIEW_READ,
        Permissions.FEEDBACK_CREATE,
        Permissions.OFFER_READ,
        Permissions.OFFER_CREATE,
        Permissions.OFFER_SUBMIT,
        Permissions.OFFER_SEND,
    ],
    Roles.HIRING_MANAGER: [
        Permissions.JOB_CREATE,
        Permissions.JOB_READ,
        Permissions.CANDIDATE_READ,
        Permissions.APPLICATION_READ,
        Permissions.INTERVIEW_READ,
        Permissions.OFFER_READ,
        Permissions.OFFER_APPROVE,
    ],
    Roles.INTERVIEWER: [
        Permissions.CANDIDATE_READ,
        Permissions.INTERVIEW_READ,
        Permissions.FEEDBACK_CREATE,
        Permissions.JOB_READ,
        Permissions.APPLICATION_READ,
    ],
}


ROLE_DATA_SCOPE: dict[str, DataScopeType] = {
    Roles.ADMIN: DataScopeType.ALL,
    Roles.HR: DataScopeType.ALL,
    Roles.HIRING_MANAGER: DataScopeType.DEPARTMENT,
    Roles.INTERVIEWER: DataScopeType.SELF,
}


def get_user_role_codes(session: Session, user: User) -> list[str]:
    stmt = (
        select(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user.id)
    )
    return list(session.exec(stmt).all())


def get_user_permissions(session: Session, user: User) -> set[str]:
    stmt = (
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user.id)
    )
    return set(session.exec(stmt).all())


def get_user_data_scope(session: Session, user: User) -> DataScopeType:
    """Return the widest data scope across all of the user's roles."""
    stmt = (
        select(DataScope.scope_type)
        .join(UserRole, UserRole.role_id == DataScope.role_id)
        .where(UserRole.user_id == user.id)
    )
    scopes = list(session.exec(stmt).all())
    if DataScopeType.ALL in scopes:
        return DataScopeType.ALL
    if DataScopeType.DEPARTMENT in scopes:
        return DataScopeType.DEPARTMENT
    if DataScopeType.SELF in scopes:
        return DataScopeType.SELF
    # Default to the most restrictive scope when none is configured.
    return DataScopeType.SELF
