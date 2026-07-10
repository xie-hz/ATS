import io

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Candidate
from tests.utils.utils import random_email


def _make_candidate(db: Session) -> Candidate:
    c = Candidate(name="Resume Candidate", email=random_email())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_resume_upload_and_resolve(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    """§14 storage: upload stores a key; download resolves to a usable URL."""
    candidate = _make_candidate(db)

    # Upload a resume (local backend by default).
    r = client.post(
        f"{settings.API_V1_STR}/admin/candidates/{candidate.id}/resume",
        headers=hr_token_headers,
        files={"file": ("cv.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # resume_url is now a storage key, not a /uploads URL.
    assert body["resume_url"].startswith("resumes/")
    assert body["resume_url"].endswith(".pdf")

    # Resolve to a directly-openable URL.
    r = client.get(
        f"{settings.API_V1_STR}/admin/candidates/{candidate.id}/resume",
        headers=hr_token_headers,
    )
    assert r.status_code == 200, r.text
    url = r.json()["url"]
    assert url.startswith("/uploads/")  # local backend
