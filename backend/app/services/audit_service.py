"""Audit log service: records key mutations for compliance/traceability."""

import uuid

from sqlmodel import Session, col, func, select

from app.models import AuditLog, AuditLogPublic, AuditLogsPublic


def log_action(
    *,
    session: Session,
    user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    before: dict | None = None,
    after: dict | None = None,
    ip: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before_data=before,
        after_data=after,
        ip=ip,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def list_audit_logs(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    resource_type: str | None = None,
) -> AuditLogsPublic:
    stmt = select(AuditLog)
    if resource_type:
        stmt = stmt.where(AuditLog.resource_type == resource_type)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(AuditLog.created_at).desc()).offset(skip).limit(limit)
    logs = session.exec(stmt).all()
    return AuditLogsPublic(
        data=[AuditLogPublic.model_validate(log) for log in logs], count=count
    )
