"""Periodic reminder tasks: interview reminders + overdue feedback.

Runs via celery beat (see app.core.celery). Dedups notifications by
(related_type, related_id, type) so repeated scans don't spam users.
"""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.core.celery import celery_app
from app.core.db import engine
from app.models import (
    Interview,
    InterviewFeedback,
    InterviewStatus,
    Notification,
)
from app.services import notification_service


def _already_notified(
    session: Session,
    related_type: str,
    related_id,
    ntype: str,
) -> bool:
    return (
        session.exec(
            select(Notification).where(
                Notification.related_type == related_type,
                Notification.related_id == related_id,
                Notification.type == ntype,
            )
        ).first()
        is not None
    )


@celery_app.task(name="app.tasks.reminders.send_reminders")
def send_reminders() -> None:
    """Scan for interviews needing reminders (idempotent via dedup)."""
    with Session(engine) as session:
        now = datetime.now(UTC)

        # 1. Upcoming interviews within 24h -> remind the interviewer.
        upcoming = session.exec(
            select(Interview).where(
                Interview.status == InterviewStatus.SCHEDULED,
                Interview.scheduled_time <= now + timedelta(hours=24),
                Interview.scheduled_time >= now,
            )
        ).all()
        for iv in upcoming:
            if not iv.interviewer_id:
                continue
            if _already_notified(session, "interview", iv.id, "interview_reminder"):
                continue
            notification_service.create_notification(
                session=session,
                user_id=iv.interviewer_id,
                type="interview_reminder",
                content=f"Interview round {iv.round} starts soon",
                related_type="interview",
                related_id=iv.id,
            )

        # 2. Completed interviews with no feedback -> nudge the interviewer.
        completed = session.exec(
            select(Interview).where(Interview.status == InterviewStatus.COMPLETED)
        ).all()
        for iv in completed:
            if not iv.interviewer_id:
                continue
            has_feedback = session.exec(
                select(InterviewFeedback).where(
                    InterviewFeedback.interview_id == iv.id
                )
            ).first()
            if has_feedback:
                continue
            if _already_notified(session, "interview", iv.id, "feedback_overdue"):
                continue
            notification_service.create_notification(
                session=session,
                user_id=iv.interviewer_id,
                type="feedback_overdue",
                content=f"Feedback pending for interview round {iv.round}",
                related_type="interview",
                related_id=iv.id,
            )
