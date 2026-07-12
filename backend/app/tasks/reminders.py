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
    InterviewStatus,
    Notification,
)
from app.services import email_service, notification_service


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
            cand_name, job_title, _ = email_service.get_app_context(
                session=session, application_id=iv.application_id
            )
            when = iv.scheduled_time.strftime("%Y-%m-%d %H:%M")
            notification_service.create_notification(
                session=session,
                user_id=iv.interviewer_id,
                type="interview_reminder",
                content=(
                    f"面试即将开始：{cand_name or '候选人'}（{job_title}）"
                    f"第 {iv.round} 轮，{when}"
                ),
                related_type="interview",
                related_id=iv.id,
            )

        # 2. SCHEDULED interviews past their time with no feedback -> nudge.
        #    An interview stays SCHEDULED until feedback is submitted (which
        #    flips it to COMPLETED), so a SCHEDULED interview whose time has
        #    passed is one awaiting evaluation. Give a 1h grace window so we
        #    don't nudge while the interview is still underway.
        overdue = session.exec(
            select(Interview).where(
                Interview.status == InterviewStatus.SCHEDULED,
                Interview.scheduled_time <= now - timedelta(hours=1),
            )
        ).all()
        for iv in overdue:
            if not iv.interviewer_id:
                continue
            if _already_notified(session, "interview", iv.id, "feedback_overdue"):
                continue
            cand_name, job_title, _ = email_service.get_app_context(
                session=session, application_id=iv.application_id
            )
            notification_service.create_notification(
                session=session,
                user_id=iv.interviewer_id,
                type="feedback_overdue",
                content=(
                    f"面试评价待提交：{cand_name or '候选人'}（{job_title}）"
                    f"第 {iv.round} 轮"
                ),
                related_type="interview",
                related_id=iv.id,
            )
