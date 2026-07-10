from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services import email_service
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


def test_candidate_emails_triggered(
    client: TestClient,
    hr_token_headers: dict[str, str],
    monkeypatch,
) -> None:
    """Enable SMTP (mocked) and verify candidate emails fire on key events."""
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test.com")
    monkeypatch.setattr(settings, "EMAILS_FROM_EMAIL", "noreply@test.com")

    send = MagicMock()
    monkeypatch.setattr(email_service, "send_email", send)

    job_id = _open_job(client, hr_token_headers, "Email Job")
    email = random_email()

    # 1. Submit (portal) -> confirmation email to the candidate.
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job_id, "name": "Tester", "email": email, "phone": "1"},
    )
    assert r.status_code == 200
    app_id = r.json()["id"]
    subjects = [c.kwargs["subject"] for c in send.call_args_list]
    assert any(e == email for c in send.call_args_list for e in [c.kwargs["email_to"]])
    assert any("申请已提交" in s for s in subjects), subjects

    # 2. Advance APPLIED -> SCREENING -> status-change email.
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app_id}/advance",
        json={"target_stage": "SCREENING"},
        headers=hr_token_headers,
    )
    assert r.status_code == 200
    subjects = [c.kwargs["subject"] for c in send.call_args_list]
    assert any("申请状态更新" in s for s in subjects), subjects

    # 3. Reject -> one more status-change email.
    before = send.call_count
    r = client.post(
        f"{settings.API_V1_STR}/admin/applications/{app_id}/reject",
        headers=hr_token_headers,
    )
    assert r.status_code == 200
    assert send.call_count == before + 1
    assert "申请状态更新" in send.call_args_list[-1].kwargs["subject"]


def test_emails_silent_when_smtp_disabled(
    client: TestClient,
    hr_token_headers: dict[str, str],
    monkeypatch,
) -> None:
    """With SMTP off, no email is sent and the operation still succeeds."""
    send = MagicMock()
    monkeypatch.setattr(email_service, "send_email", send)
    job_id = _open_job(client, hr_token_headers, "Silent Job")
    r = client.post(
        f"{settings.API_V1_STR}/portal/applications/",
        json={"job_id": job_id, "name": "X", "email": random_email()},
    )
    assert r.status_code == 200
    assert send.call_count == 0  # _send short-circuited before calling send_email
