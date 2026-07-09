"""Admin analytics summary."""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import AnalyticsSummary
from app.services import analytics_service

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    dependencies=[Depends(require_permission(Permissions.APPLICATION_READ))],
)
def get_summary(session: SessionDep) -> Any:
    return analytics_service.get_summary(session=session)
