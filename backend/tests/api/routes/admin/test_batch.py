from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import (
    Application,
    ApplicationStage,
    Candidate,
    Job,
    JobStatus,
)
from tests.utils.user import create_user_with_role
from tests.utils.utils import random_email


def _make_application(db: Session, owner_id=None) -> Application:
    job = Job(title="Batch Job", headcount=5, status=JobStatus.OPEN)
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
        owner_id=owner_id,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def test_batch_invite_interview(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    """§16 batch invite: one interview per application, spaced by interval."""
    interviewer, _ = create_user_with_role(db=db, role_code="interviewer")
    app1 = _make_application(db)
    app2 = _make_application(db)

    start = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    r = client.post(
        f"{settings.API_V1_STR}/admin/interviews/batch",
        json={
            "application_ids": [str(app1.id), str(app2.id)],
            "interviewer_id": str(interviewer.id),
            "round": 1,
            "scheduled_time": start,
            "interval_minutes": 60,
        },
        headers=hr_token_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert len(data["created"]) == 2
    assert data["errors"] == []
    # Spacing: second slot is 60 min after the first.
    t0 = datetime.fromisoformat(data["created"][0]["scheduled_time"])
    t1 = datetime.fromisoformat(data["created"][1]["scheduled_time"])
    assert abs((t1 - t0).total_seconds() - 3600) < 1
    # Applications advanced to INTERVIEW.
    db.refresh(app1)
    db.refresh(app2)
    assert app1.stage == ApplicationStage.INTERVIEW
    assert app2.stage == ApplicationStage.INTERVIEW


def test_batch_notify(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    """§16 batch notify: owners of selected applications get a notification."""
    owner, _ = create_user_with_role(db=db, role_code="hr")
    app1 = _make_application(db, owner_id=owner.id)
    app2 = _make_application(db, owner_id=owner.id)
    app_no_owner = _make_application(db)  # should be skipped

    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/batch-notify",
        json={
            "application_ids": [
                str(app1.id),
                str(app2.id),
                str(app_no_owner.id),
            ],
            "message": "Please review these candidates.",
        },
        headers=hr_token_headers,
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["notified"] == 2
    assert data["skipped"] == 1
