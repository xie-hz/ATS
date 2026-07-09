"""Admin audit log viewing (admin only)."""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import AuditLogsPublic
from app.services import audit_service

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit-logs"])


@router.get(
    "/",
    response_model=AuditLogsPublic,
    dependencies=[Depends(require_permission(Permissions.USER_MANAGE))],
)
def list_audit_logs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    resource_type: str | None = None,
) -> Any:
    # Admin-only: pass a system user marker; data scope is ALL for admins.
    return audit_service.list_audit_logs(
        session=session,
        skip=skip,
        limit=limit,
        resource_type=resource_type,
    )
