"""Interview service: scheduling, calendar, and feedback."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.models import (
    Application,
    ApplicationStage,
    BatchInterviewCreate,
    BatchInterviewError,
    BatchInterviewResult,
    Candidate,
    DataScopeType,
    FeedbackCreate,
    Interview,
    InterviewCreate,
    InterviewFeedback,
    InterviewPublic,
    InterviewsPublic,
    InterviewStatus,
    Job,
    User,
)
from app.services import easymeeting_service, email_service, notification_service
from app.services.base import get_scope, not_found


def _scoped(session: Session, user: User):
    stmt = select(Interview)
    scope = get_scope(session, user)
    if scope == DataScopeType.DEPARTMENT:
        stmt = (
            stmt.join(Application, Application.id == Interview.application_id)
            .join(Job, Job.id == Application.job_id)
            .where(Job.department_id == user.department_id)
        )
    elif scope == DataScopeType.SELF:
        stmt = stmt.where(Interview.interviewer_id == user.id)
    return stmt


def to_public_list(
    *, session: Session, interviews: list[Interview]
) -> list[InterviewPublic]:
    """Build InterviewPublic with denormalized candidate_name/job_title/job_id.

    Batched (3 extra queries) so listing many interviews stays cheap. The
    denormalized fields let the UI render names/titles without separate,
    permission-scoped candidate/job listings (which interviewers can't fully
    see).
    """
    if not interviews:
        return []
    app_ids = [iv.application_id for iv in interviews]
    apps = {
        a.id: a
        for a in session.exec(
            select(Application).where(col(Application.id).in_(app_ids))
        ).all()
    }
    cand_ids = {a.candidate_id for a in apps.values()}
    cands = {
        c.id: c.name
        for c in session.exec(
            select(Candidate).where(col(Candidate.id).in_(list(cand_ids)))
        ).all()
    } if cand_ids else {}
    job_ids = {a.job_id for a in apps.values()}
    jobs = {
        j.id: j.title
        for j in session.exec(
            select(Job).where(col(Job.id).in_(list(job_ids)))
        ).all()
    } if job_ids else {}
    result: list[InterviewPublic] = []
    for iv in interviews:
        app = apps.get(iv.application_id)
        result.append(
            InterviewPublic.model_validate(
                iv,
                update={
                    "candidate_name": cands.get(app.candidate_id, "") if app else "",
                    "job_title": jobs.get(app.job_id, "") if app else "",
                    "job_id": app.job_id if app else None,
                },
            )
        )
    return result


def to_public(*, session: Session, iv: Interview) -> InterviewPublic:
    return to_public_list(session=session, interviews=[iv])[0]


def list_interviews(
    *,
    session: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    interview_status: InterviewStatus | None = None,
) -> InterviewsPublic:
    stmt = _scoped(session, user)
    if interview_status:
        stmt = stmt.where(Interview.status == interview_status)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = (
        stmt.order_by(col(Interview.scheduled_time).desc()).offset(skip).limit(limit)
    )
    interviews = session.exec(stmt).all()
    return InterviewsPublic(
        data=to_public_list(session=session, interviews=interviews), count=count
    )


def get_interview(
    *, session: Session, user: User, interview_id: uuid.UUID
) -> Interview:
    stmt = _scoped(session, user).where(Interview.id == interview_id)
    iv = session.exec(stmt).first()
    if not iv:
        raise not_found("Interview")
    return iv


def create_interview(
    *, session: Session, interview_in: InterviewCreate, host_email: str | None = None
) -> Interview:
    if not session.get(Application, interview_in.application_id):
        raise not_found("Application")
    # 同申请同 round 不重复创建（SCHEDULED 状态）
    existing_round = session.exec(
        select(Interview).where(
            Interview.application_id == interview_in.application_id,
            Interview.round == interview_in.round,
            Interview.status == InterviewStatus.SCHEDULED,
        )
    ).first()
    if existing_round:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该申请已安排第 {interview_in.round} 轮面试，请先完成或取消",
        )
    # 检查面试官时间冲突（±30分钟）
    if interview_in.interviewer_id:
        from datetime import timedelta

        conflict = session.exec(
            select(Interview).where(
                Interview.interviewer_id == interview_in.interviewer_id,
                Interview.status == InterviewStatus.SCHEDULED,
                Interview.scheduled_time
                >= interview_in.scheduled_time - timedelta(minutes=30),
                Interview.scheduled_time
                <= interview_in.scheduled_time + timedelta(minutes=30),
            )
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该面试官在该时间段已有面试安排，请错开至少30分钟",
            )
    iv = Interview.model_validate(
        interview_in, update={"status": InterviewStatus.SCHEDULED}
    )
    session.add(iv)
    session.commit()
    session.refresh(iv)
    # Resolve candidate/job context once for the notification + emails.
    cand_name, job_title, cand_email = email_service.get_app_context(
        session=session, application_id=iv.application_id
    )
    # Create an EasyMeeting video room for this interview (non-fatal: if
    # EasyMeeting is down the interview is still scheduled, just no meeting link).
    meeting = easymeeting_service.create_meeting(
        ats_business_id=str(iv.id),
        meeting_name=f"{job_title} 第{iv.round}轮面试",
        start_time=iv.scheduled_time,
        host_email=host_email,
    )
    if meeting:
        iv.meeting_id = meeting["meeting_id"]
        iv.meeting_no = meeting["meeting_no"]
        iv.meeting_password = meeting["meeting_password"]
        session.add(iv)
        session.commit()
        session.refresh(iv)
    when = iv.scheduled_time.strftime("%Y-%m-%d %H:%M")
    # Notify the assigned interviewer (in-app).
    if iv.interviewer_id:
        notification_service.create_notification(
            session=session,
            user_id=iv.interviewer_id,
            type="interview_scheduled",
            content=(
                f"新面试安排：{cand_name or '候选人'} 应聘「{job_title}」，"
                f"第 {iv.round} 轮，{when}"
            ),
            related_type="interview",
            related_id=iv.id,
        )
        # Also email the interviewer.
        interviewer = session.get(User, iv.interviewer_id)
        if interviewer and interviewer.email:
            email_service.send_interview_assigned_email(
                email_to=interviewer.email,
                recipient_name=interviewer.name,
                candidate_name=cand_name or "候选人",
                job_title=job_title,
                scheduled_time=iv.scheduled_time,
                round=iv.round,
                meeting_no=iv.meeting_no,
                meeting_password=iv.meeting_password,
            )
    # 安排面试后，申请自动进入面试阶段
    app = session.get(Application, iv.application_id)
    if app and app.stage not in (
        ApplicationStage.INTERVIEW,
        ApplicationStage.OFFER,
        ApplicationStage.HIRED,
    ):
        app.stage = ApplicationStage.INTERVIEW
        session.add(app)
        session.commit()
    # Notify the candidate of the scheduled interview.
    if cand_email:
        email_service.send_interview_scheduled_email(
            email_to=cand_email,
            recipient_name=cand_name,
            job_title=job_title,
            scheduled_time=iv.scheduled_time,
            round=iv.round,
            meeting_no=iv.meeting_no,
            meeting_password=iv.meeting_password,
        )
    return iv


def list_calendar(*, session: Session, user: User) -> list[InterviewPublic]:
    """Upcoming interviews the caller is assigned to conduct."""
    stmt = (
        select(Interview)
        .where(Interview.interviewer_id == user.id)
        .where(Interview.scheduled_time >= datetime.now(UTC))
        .order_by(col(Interview.scheduled_time).asc())
    )
    interviews = session.exec(stmt).all()
    return to_public_list(session=session, interviews=interviews)


def get_feedback(
    *, session: Session, interview_id: uuid.UUID
) -> InterviewFeedback | None:
    return session.exec(
        select(InterviewFeedback).where(
            InterviewFeedback.interview_id == interview_id
        )
    ).first()


def cancel_interview(
    *, session: Session, user: User, interview_id: uuid.UUID
) -> Interview:
    from app.core.state_machines import assert_interview_transition

    iv = get_interview(session=session, user=user, interview_id=interview_id)
    assert_interview_transition(iv.status, InterviewStatus.CANCELLED)
    iv.status = InterviewStatus.CANCELLED
    session.add(iv)
    session.commit()
    session.refresh(iv)
    # 同步取消 EasyMeeting 视频会议（非致命）
    if iv.meeting_id:
        easymeeting_service.cancel_meeting(meeting_id=iv.meeting_id)
    # 取消面试后，如果申请在面试阶段且没有其他活跃面试，回筛选
    app = session.get(Application, iv.application_id)
    if app and app.stage == ApplicationStage.INTERVIEW:
        other = session.exec(
            select(Interview).where(
                Interview.application_id == app.id,
                Interview.id != iv.id,
                Interview.status.in_([
                    InterviewStatus.SCHEDULED,
                    InterviewStatus.COMPLETED,
                ]),
            )
        ).first()
        if not other:
            app.stage = ApplicationStage.SCREENING
            session.add(app)
            session.commit()
    # Notify the candidate the interview was cancelled.
    cand_name, job_title, email = email_service.get_app_context(
        session=session, application_id=iv.application_id
    )
    if email:
        email_service.send_interview_cancelled_email(
            email_to=email,
            recipient_name=cand_name,
            job_title=job_title,
            scheduled_time=iv.scheduled_time,
            round=iv.round,
        )
    return iv


def update_interview(
    *,
    session: Session,
    user: User,
    interview_id: uuid.UUID,
    interviewer_id: uuid.UUID | None = None,
    scheduled_time: datetime | None = None,
    round: int | None = None,
) -> Interview:
    """Update an interview (only SCHEDULED interviews can be edited)."""
    iv = get_interview(session=session, user=user, interview_id=interview_id)
    if iv.status != InterviewStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能编辑待面试状态的面试",
        )
    if interviewer_id is not None:
        iv.interviewer_id = interviewer_id
    if scheduled_time is not None:
        # 检查新时间是否冲突
        from datetime import timedelta

        conflict = session.exec(
            select(Interview).where(
                Interview.interviewer_id == iv.interviewer_id,
                Interview.id != iv.id,
                Interview.status == InterviewStatus.SCHEDULED,
                Interview.scheduled_time
                >= scheduled_time - timedelta(minutes=30),
                Interview.scheduled_time
                <= scheduled_time + timedelta(minutes=30),
            )
        ).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该面试官在该时间段已有面试安排，请错开至少30分钟",
            )
        iv.scheduled_time = scheduled_time
    if round is not None:
        iv.round = round
    session.add(iv)
    session.commit()
    session.refresh(iv)
    return iv


def submit_feedback(
    *,
    session: Session,
    user: User,
    interview_id: uuid.UUID,
    feedback_in: FeedbackCreate,
) -> InterviewFeedback:
    iv = get_interview(session=session, user=user, interview_id=interview_id)
    existing = session.exec(
        select(InterviewFeedback).where(InterviewFeedback.interview_id == iv.id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback already exists for this interview",
        )
    feedback = InterviewFeedback.model_validate(
        feedback_in, update={"interview_id": iv.id}
    )
    session.add(feedback)
    if iv.status == InterviewStatus.SCHEDULED:
        iv.status = InterviewStatus.COMPLETED
        session.add(iv)
    session.commit()
    session.refresh(feedback)
    return feedback


def batch_create_interviews(
    *, session: Session, batch_in: BatchInterviewCreate
) -> BatchInterviewResult:
    """§16 batch invite: one interview per application, spaced by interval.

    Reuses create_interview per item (conflict + round-dup checks, stage
    advancement, interviewer notification) and collects per-item errors so a
    single bad application doesn't abort the whole batch.
    """
    from datetime import timedelta

    result = BatchInterviewResult()
    # De-duplicate while preserving order.
    seen: set[uuid.UUID] = set()
    unique_ids = [aid for aid in batch_in.application_ids if not (aid in seen or seen.add(aid))]  # type: ignore[func-returns-value]

    for i, app_id in enumerate(unique_ids):
        slot = batch_in.scheduled_time + timedelta(
            minutes=i * batch_in.interval_minutes
        )
        try:
            iv = create_interview(
                session=session,
                interview_in=InterviewCreate(
                    application_id=app_id,
                    interviewer_id=batch_in.interviewer_id,
                    round=batch_in.round,
                    scheduled_time=slot,
                ),
            )
            result.created.append(InterviewPublic.model_validate(iv))
        except HTTPException as exc:
            result.errors.append(
                BatchInterviewError(
                    application_id=app_id, detail=str(exc.detail)
                )
            )
    return result
