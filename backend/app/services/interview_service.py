"""Interview service: scheduling, calendar, and feedback."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.models import (
    Application,
    ApplicationStage,
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
from app.services import notification_service
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
        data=[InterviewPublic.model_validate(i) for i in interviews], count=count
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
    *, session: Session, interview_in: InterviewCreate
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
    # Notify the assigned interviewer.
    if iv.interviewer_id:
        notification_service.create_notification(
            session=session,
            user_id=iv.interviewer_id,
            type="interview_scheduled",
            content=f"New interview scheduled (round {iv.round})",
            related_type="interview",
            related_id=iv.id,
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
    return [InterviewPublic.model_validate(i) for i in interviews]


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
