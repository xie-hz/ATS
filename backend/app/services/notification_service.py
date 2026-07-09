"""Notification service: in-app notifications for internal users."""

import uuid

from sqlmodel import Session, col, func, select

from app.models import (
    Notification,
    NotificationPublic,
    NotificationsPublic,
    User,
)
from app.services.base import not_found


def create_notification(
    *,
    session: Session,
    user_id: uuid.UUID,
    type: str,
    content: str,
    related_type: str | None = None,
    related_id: uuid.UUID | None = None,
) -> Notification:
    n = Notification(
        user_id=user_id,
        type=type,
        content=content,
        related_type=related_type,
        related_id=related_id,
    )
    session.add(n)
    session.commit()
    session.refresh(n)
    return n


def list_notifications(
    *,
    session: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
) -> NotificationsPublic:
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.read_status == False)  # noqa: E712
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = (
        stmt.order_by(col(Notification.created_at).desc()).offset(skip).limit(limit)
    )
    ns = session.exec(stmt).all()
    return NotificationsPublic(
        data=[NotificationPublic.model_validate(n) for n in ns], count=count
    )


def mark_read(
    *, session: Session, user: User, notification_id: uuid.UUID
) -> Notification:
    n = session.exec(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    ).first()
    if not n:
        raise not_found("Notification")
    n.read_status = True
    session.add(n)
    session.commit()
    session.refresh(n)
    return n


def mark_all_read(*, session: Session, user: User) -> int:
    ns = session.exec(
        select(Notification).where(
            Notification.user_id == user.id,
            Notification.read_status == False,  # noqa: E712
        )
    ).all()
    for n in ns:
        n.read_status = True
    session.add_all(ns)
    session.commit()
    return len(ns)
