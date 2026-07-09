"""Admin notifications: list + mark read."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, NotificationPublic, NotificationsPublic
from app.services import notification_service

router = APIRouter(prefix="/admin/notifications", tags=["admin-notifications"])


@router.get("/", response_model=NotificationsPublic)
def list_notifications(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> Any:
    return notification_service.list_notifications(
        session=session,
        user=current_user,
        skip=skip,
        limit=limit,
        unread_only=unread_only,
    )


@router.post("/{notification_id}/read", response_model=NotificationPublic)
def mark_read(
    session: SessionDep,
    current_user: CurrentUser,
    notification_id: uuid.UUID,
) -> Any:
    n = notification_service.mark_read(
        session=session, user=current_user, notification_id=notification_id
    )
    return NotificationPublic.model_validate(n)


@router.post("/read-all", response_model=Message)
def mark_all_read(session: SessionDep, current_user: CurrentUser) -> Any:
    count = notification_service.mark_all_read(session=session, user=current_user)
    return Message(message=f"{count} notifications marked as read")
