from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import (
    Application,
    ApplicationStage,
    Candidate,
    Interview,
    InterviewStatus,
    Job,
    JobStatus,
)
from tests.utils.utils import random_email


def test_summary_pending_counts(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    """Dashboard §16: pending_candidates + pending_feedback are reported."""
    job = Job(title="Summary Job", headcount=1, status=JobStatus.OPEN)
    db.add(job)
    db.commit()
    db.refresh(job)
    candidate = Candidate(name="C", email=random_email())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    app = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        stage=ApplicationStage.APPLIED,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # A SCHEDULED interview whose time has passed -> counts as pending
    # feedback (the interview should have concluded but no feedback yet).
    iv = Interview(
        application_id=app.id,
        round=1,
        scheduled_time=datetime.now(UTC) - timedelta(hours=2),
        status=InterviewStatus.SCHEDULED,
    )
    db.add(iv)
    db.commit()

    r = client.get(
        f"{settings.API_V1_STR}/admin/analytics/summary",
        headers=hr_token_headers,
    )
    assert r.status_code == 200
    data = r.json()

    assert data["funnel"]["APPLIED"] >= 1
    assert data["pending_candidates"] >= 1  # the APPLIED application
    assert data["pending_feedback"] >= 1  # the past SCHEDULED interview
