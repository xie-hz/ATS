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
from tests.utils.utils import random_email


def _make_application(db: Session) -> Application:
    job = Job(title="Test Job", headcount=1, status=JobStatus.OPEN)
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
    return app


def test_application_advance_reject_restore(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    app = _make_application(db)

    # APPLIED -> SCREENING
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app.id}/advance",
        json={"target_stage": "SCREENING"},
        headers=hr_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["stage"] == "SCREENING"

    # SCREENING -> REJECTED
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app.id}/reject",
        headers=hr_token_headers,
    )
    assert r.json()["stage"] == "REJECTED"

    # REJECTED -> SCREENING (restore)
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app.id}/restore",
        headers=hr_token_headers,
    )
    assert r.json()["stage"] == "SCREENING"


def test_application_invalid_transition(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    app = _make_application(db)
    # APPLIED -> HIRED is not allowed (must go through the funnel)
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app.id}/advance",
        json={"target_stage": "HIRED"},
        headers=hr_token_headers,
    )
    assert r.status_code == 400


def test_restore_non_rejected_fails(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    app = _make_application(db)  # APPLIED
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app.id}/restore",
        headers=hr_token_headers,
    )
    assert r.status_code == 400
