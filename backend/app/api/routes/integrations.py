"""Integration webhooks from external systems (e.g. EasyMeeting).

EasyMeeting calls back here when an interview meeting ends or is cancelled,
so ATS can update the interview status.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Body

from app.api.deps import SessionDep
from app.models import Interview, InterviewStatus

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/easymeeting/webhook")
def easymeeting_webhook(
    session: SessionDep,
    payload: Annotated[dict[str, Any], Body()],
) -> Any:
    """Receive EasyMeeting meeting events.

    Payload: {event: "FINISHED"|"CANCELLED", meetingId, atsBusinessId, status}
    atsBusinessId is the ATS interview id (passed when the meeting was created).
    """
    event = (payload.get("event") or "").upper()
    ats_business_id = payload.get("atsBusinessId")
    if not ats_business_id:
        return {"status": "ignored", "reason": "no atsBusinessId"}

    try:
        iv = session.get(Interview, ats_business_id)
    except Exception:
        # atsBusinessId 不是合法 UUID 等情况，忽略而非 500
        return {"status": "ignored", "reason": "invalid atsBusinessId"}
    if iv is None:
        # Ack so EasyMeeting doesn't retry; nothing to update.
        return {"status": "ignored", "reason": "interview not found"}

    if event == "FINISHED":
        # Meeting ended -> mark interview conducted (COMPLETED). Feedback can
        # still be submitted afterwards (submit_feedback is idempotent on status).
        if iv.status == InterviewStatus.SCHEDULED:
            iv.status = InterviewStatus.COMPLETED
            session.add(iv)
            session.commit()
    elif event == "CANCELLED":
        if iv.status == InterviewStatus.SCHEDULED:
            iv.status = InterviewStatus.CANCELLED
            session.add(iv)
            session.commit()

    return {"status": "ok", "interview_status": iv.status}
