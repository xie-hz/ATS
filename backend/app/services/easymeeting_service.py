"""EasyMeeting integration client.

When an interview is scheduled, ATS calls EasyMeeting's open API to create a
video meeting and stores the meeting no/password on the interview. When an
interview is cancelled, ATS asks EasyMeeting to cancel the meeting.

All calls are non-fatal: if EasyMeeting is unreachable, the interview is still
created (just without a meeting link) and a warning is logged. The video
interview is an enhancement, not a hard dependency of the hiring flow.
"""

from __future__ import annotations

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Default join type for interview meetings: PASSWORD (1).
_JOIN_TYPE_PASSWORD = 1


def create_meeting(*, ats_business_id: str, meeting_name: str, start_time=None, host_email: str | None = None) -> dict | None:
    """Create an EasyMeeting interview meeting.

    host_email: the current HR's email. EasyMeeting looks it up in user_info
    to find the userId (host). If not found, falls back to admin.
    start_time: the interview's scheduled time (datetime), for the 1-hour window.
    """
    try:
        form_data = {
            "hostEmail": host_email or settings.EASYMEETING_HOST_USER_ID,
            "meetingName": meeting_name,
            "joinType": _JOIN_TYPE_PASSWORD,
            "joinPassword": _gen_password(),
            "atsBusinessId": ats_business_id,
        }
        if start_time:
            form_data["startTime"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        resp = httpx.post(
            f"{settings.EASYMEETING_API_URL}/create",
            headers={"X-API-Key": settings.EASYMEETING_API_KEY},
            data=form_data,
            timeout=5.0,
        )
        body = resp.json()
        if resp.status_code == 200 and body.get("status") == "success":
            data = body.get("data") or {}
            return {
                "meeting_id": data.get("meetingId"),
                "meeting_no": data.get("meetingNo"),
                "meeting_password": data.get("joinPassword"),
            }
        logger.warning(
            "easymeeting_create_failed",
            status=resp.status_code,
            info=body.get("info"),
        )
    except Exception as exc:  # noqa: BLE001 - non-fatal
        logger.warning("easymeeting_create_error", error=str(exc))
    return None


def cancel_meeting(*, meeting_id: str) -> None:
    """Cancel an EasyMeeting meeting (non-fatal)."""
    if not meeting_id:
        return
    try:
        resp = httpx.post(
            f"{settings.EASYMEETING_API_URL}/cancel",
            headers={"X-API-Key": settings.EASYMEETING_API_KEY},
            data={"meetingId": meeting_id},
            timeout=5.0,
        )
        if resp.status_code != 200:
            logger.warning(
                "easymeeting_cancel_failed",
                status=resp.status_code,
                meeting_id=meeting_id,
            )
    except Exception as exc:  # noqa: BLE001 - non-fatal
        logger.warning("easymeeting_cancel_error", error=str(exc), meeting_id=meeting_id)


def _gen_password() -> str:
    """Generate a short numeric meeting password."""
    import random

    return "".join(random.choice("0123456789") for _ in range(4))
