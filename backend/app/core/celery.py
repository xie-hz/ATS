"""Celery application + beat schedule for async tasks (email, reminders)."""

from celery import Celery
from celery.schedules import schedule

from app.core.config import settings

celery_app = Celery(
    "ats",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.reminders"],
)

celery_app.conf.update(
    task_default_queue="ats",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Periodically scan for interviews needing reminders / overdue feedback.
        "send-reminders-every-15-min": {
            "task": "app.tasks.reminders.send_reminders",
            "schedule": schedule(run_every=900),  # 15 minutes
        },
    },
)


def get_celery_app() -> Celery:
    return celery_app
