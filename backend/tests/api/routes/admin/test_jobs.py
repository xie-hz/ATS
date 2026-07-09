from fastapi.testclient import TestClient

from app.core.config import settings


def test_hr_create_job(client: TestClient, hr_token_headers: dict[str, str]) -> None:
    body = {
        "title": "Python Engineer",
        "headcount": 2,
        "salary_min": 10000,
        "salary_max": 20000,
        "location": "Remote",
        "description": "Build things",
        "requirements": "Python",
    }
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/", json=body, headers=hr_token_headers
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "DRAFT"
    assert data["title"] == "Python Engineer"
    assert data["headcount"] == 2


def test_interviewer_cannot_create_job(
    client: TestClient, interviewer_token_headers: dict[str, str]
) -> None:
    body = {"title": "Should Fail", "headcount": 1}
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/",
        json=body,
        headers=interviewer_token_headers,
    )
    assert r.status_code == 403


def test_job_publish_and_close_flow(
    client: TestClient, hr_token_headers: dict[str, str]
) -> None:
    body = {"title": "Flow Job", "headcount": 1}
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/", json=body, headers=hr_token_headers
    )
    job_id = r.json()["id"]

    # DRAFT -> PENDING_APPROVAL
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/{job_id}/publish",
        headers=hr_token_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "PENDING_APPROVAL"

    # PENDING_APPROVAL -> OPEN
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/{job_id}/publish",
        headers=hr_token_headers,
    )
    assert r.json()["status"] == "OPEN"

    # OPEN -> CLOSED
    r = client.post(
        f"{settings.API_V1_STR}/admin/jobs/{job_id}/close",
        headers=hr_token_headers,
    )
    assert r.json()["status"] == "CLOSED"


def test_hr_list_jobs(client: TestClient, hr_token_headers: dict[str, str]) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admin/jobs/", headers=hr_token_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "count" in body
