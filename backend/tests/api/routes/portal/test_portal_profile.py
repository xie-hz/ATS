from fastapi.testclient import TestClient
from sqlmodel import Session, col, select

from app.core.config import settings
from app.models import EmailVerificationCode
from tests.utils.utils import random_email


def _open_job(client: TestClient, headers: dict[str, str], title: str) -> str:
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/",
        json={"title": title, "headcount": 1},
        headers=headers,
    )
    job_id = r.json()["id"]
    for _ in range(2):  # DRAFT -> PENDING_APPROVAL -> OPEN
        client.post(
            f"{settings.API_V1_STR}/admin/jobs/{job_id}/publish", headers=headers
        )
    return job_id


def _portal_token(client: TestClient, db: Session, email: str) -> str:
    client.post(f"{settings.API_V1_STR}/portal/auth/send-code", json={"email": email})
    code = db.exec(
        select(EmailVerificationCode)
        .where(EmailVerificationCode.email == email)
        .order_by(col(EmailVerificationCode.created_at).desc())
    ).first()
    r = client.post(
        f"{settings.API_V1_STR}/portal/auth/verify",
        json={"email": email, "code": code.code},
    )
    return r.json()["access_token"]


def test_portal_profile_and_submit_updates_candidate(
    client: TestClient, db: Session, hr_token_headers: dict[str, str]
) -> None:
    job1 = _open_job(client, hr_token_headers, "Profile Job 1")
    job2 = _open_job(client, hr_token_headers, "Profile Job 2")
    email = random_email()
    portal_headers = lambda: {  # noqa: E731
        "Authorization": f"Bearer {_portal_token(client, db, email)}"
    }

    # 1. First application creates the candidate (name V1, phone 111).
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job1, "name": "V1", "email": email, "phone": "111"},
    )
    assert r.status_code == 200

    # 2. Re-apply with edited info -> candidate record is updated.
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job2, "name": "V2", "email": email, "phone": "222"},
    )
    assert r.status_code == 200

    # 3. GET /portal/me reflects the updated profile.
    r = client.get(f"{settings.API_V1_STR}/portal/me/", headers=portal_headers())
    assert r.status_code == 200
    me = r.json()
    assert me["email"] == email
    assert me["name"] == "V2"
    assert me["phone"] == "222"

    # 4. PATCH /portal/me updates name/phone.
    r = client.patch(
        f"{settings.API_V1_STR}/portal/me/",
        headers=portal_headers(),
        json={"name": "V3", "phone": "333"},
    )
    assert r.status_code == 200
    assert r.json()["name"] == "V3"
    assert r.json()["phone"] == "333"


def test_portal_profile_not_found(
    client: TestClient, db: Session
) -> None:
    """Logged in but never applied -> no candidate record -> 404."""
    email = random_email()
    token = _portal_token(client, db, email)
    r = client.get(
        f"{settings.API_V1_STR}/portal/me/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404
