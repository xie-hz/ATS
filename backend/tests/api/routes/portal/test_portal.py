from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utils import random_email


def test_portal_submit_and_track(
    client: TestClient, hr_token_headers: dict[str, str], fake_redis
) -> None:
    # Create and open a job via admin API.
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/",
        json={"title": "Portal Job", "headcount": 1},
        headers=hr_token_headers,
    )
    job_id = r.json()["id"]
    client.post(
        f"{settings.API_V1_STR}/admin/jobs/{job_id}/publish", headers=hr_token_headers
    )
    client.post(
        f"{settings.API_V1_STR}/admin/jobs/{job_id}/publish", headers=hr_token_headers
    )

    # Public: list open jobs.
    r = client.get(f"{settings.API_V1_STR}/portal/jobs/")
    assert r.status_code == 200
    assert any(j["id"] == job_id for j in r.json()["data"])

    # Submit an application.
    email = random_email()
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job_id, "name": "Applicant", "email": email, "phone": "123"},
    )
    assert r.status_code == 200
    app_id = r.json()["id"]
    assert r.json()["stage"] == "APPLIED"

    # Duplicate application is rejected.
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job_id, "name": "Applicant", "email": email},
    )
    assert r.status_code == 400

    # Request a verification code.
    r = client.post(
        f"{settings.API_V1_STR}/portal/auth/send-code", json={"email": email}
    )
    assert r.status_code == 200

    # Read the code from Redis (fake) -- it's no longer stored in the DB.
    code = fake_redis.get(f"portal:code:{email}")
    assert code is not None

    # Verify code -> portal token.
    r = client.post(
        f"{settings.API_V1_STR}/portal/auth/verify",
        json={"email": email, "code": code},
    )
    assert r.status_code == 200
    portal_token = r.json()["access_token"]

    # List own applications with the portal token.
    r = client.get(
        f"{settings.API_V1_STR}/portal/applications/",
        headers={"Authorization": f"Bearer {portal_token}"},
    )
    assert r.status_code == 200
    assert any(a["id"] == app_id for a in r.json())

    # Wrong code is rejected.
    r = client.post(
        f"{settings.API_V1_STR}/portal/auth/verify",
        json={"email": email, "code": "000000"},
    )
    assert r.status_code == 400


def test_portal_job_not_open_rejects_application(
    client: TestClient, hr_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/",
        json={"title": "Closed Job", "headcount": 1},
        headers=hr_token_headers,
    )
    job_id = r.json()["id"]  # status DRAFT
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job_id, "name": "X", "email": random_email()},
    )
    assert r.status_code == 400
