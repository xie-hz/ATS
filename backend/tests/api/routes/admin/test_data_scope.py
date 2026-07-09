from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Candidate
from tests.utils.utils import random_email


def test_hr_sees_all_candidates(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    candidate = Candidate(name="Visible", email=random_email())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    r = client.get(
        f"{settings.API_V1_STR}/admin/candidates/", headers=hr_token_headers
    )
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()["data"]]
    assert str(candidate.id) in ids


def test_interviewer_sees_only_assigned(
    client: TestClient, db: Session, interviewer_token_headers: dict[str, str]
) -> None:
    # Candidate with no interview assigned to the interviewer.
    candidate = Candidate(name="Hidden", email=random_email())
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    r = client.get(
        f"{settings.API_V1_STR}/admin/candidates/",
        headers=interviewer_token_headers,
    )
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()["data"]]
    assert str(candidate.id) not in ids


def test_unauthenticated_candidate_list(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/admin/candidates/")
    assert r.status_code == 401
