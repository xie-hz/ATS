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

    # FINISHED（会议结束）：仅 ack，不推进面试状态。面试应保持 SCHEDULED，直到
    # 面试官提交评价（submit_feedback）才进入 COMPLETED。若提前置 COMPLETED，看板
    # 会误显示"已评价/详情"，分析与"催评价"提醒也会被绕过（二者均按
    # SCHEDULED + 已过预约时间 = 待评价 工作）。会议结束不等于已评价。
    if event == "CANCELLED" and iv.status == InterviewStatus.SCHEDULED:
        iv.status = InterviewStatus.CANCELLED
        session.add(iv)
        session.commit()

    return {"status": "ok", "interview_status": iv.status}
