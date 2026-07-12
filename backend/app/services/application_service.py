"""Application service: data-scope filtering + application stage machine."""

import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.core.state_machines import assert_application_transition
from app.models import (
    Application,
    ApplicationPublic,
    ApplicationsPublic,
    ApplicationStage,
    BatchNotify,
    BatchNotifyResult,
    Candidate,
    DataScopeType,
    Interview,
    Job,
    Offer,
    OfferStatus,
    User,
)
from app.services import audit_service, email_service, notification_service
from app.services.base import get_scope, not_found


def _scoped(session: Session, user: User):
    stmt = select(Application)
    scope = get_scope(session, user)
    if scope == DataScopeType.DEPARTMENT:
        stmt = (
            stmt.join(Job, Job.id == Application.job_id)
            .where(Job.department_id == user.department_id)
        )
    elif scope == DataScopeType.SELF:
        stmt = (
            stmt.join(Interview, Interview.application_id == Application.id)
            .where(Interview.interviewer_id == user.id)
            .distinct()
        )
    return stmt


def list_applications(
    *,
    session: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    stage: ApplicationStage | None = None,
    job_id: uuid.UUID | None = None,
) -> ApplicationsPublic:
    stmt = _scoped(session, user)
    if stage:
        stmt = stmt.where(Application.stage == stage)
    if job_id:
        stmt = stmt.where(Application.job_id == job_id)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(Application.created_at).desc()).offset(skip).limit(limit)
    apps = session.exec(stmt).all()
    return ApplicationsPublic(
        data=[ApplicationPublic.model_validate(a) for a in apps], count=count
    )


def get_application(
    *, session: Session, user: User, application_id: uuid.UUID
) -> Application:
    stmt = _scoped(session, user).where(Application.id == application_id)
    app = session.exec(stmt).first()
    if not app:
        raise not_found("Application")
    return app


def create_application(
    *, session: Session, user: User, candidate_id: uuid.UUID, job_id: uuid.UUID,
    source: str | None = None,
) -> Application:
    if not session.get(Candidate, candidate_id):
        raise not_found("Candidate")
    job = session.get(Job, job_id)
    if not job:
        raise not_found("Job")
    # 同候选人+同职位不重复创建（未淘汰的）
    existing = session.exec(
        select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_id == job_id,
            Application.stage != ApplicationStage.REJECTED,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该候选人已申请该职位，请勿重复创建",
        )
    app = Application(
        candidate_id=candidate_id,
        job_id=job_id,
        stage=ApplicationStage.APPLIED,
        source=source,
        owner_id=user.id,
    )
    session.add(app)
    session.commit()
    session.refresh(app)
    return app


def advance_application(
    *,
    session: Session,
    user: User,
    application_id: uuid.UUID,
    target_stage: ApplicationStage,
) -> Application:
    app = get_application(session=session, user=user, application_id=application_id)
    before = {"stage": app.stage.value}
    # 进入流程（面试/Offer/入职）时，检查候选人是否已在其他申请中
    if target_stage in (
        ApplicationStage.INTERVIEW,
        ApplicationStage.OFFER,
        ApplicationStage.HIRED,
    ):
        in_progress = session.exec(
            select(Application).where(
                Application.candidate_id == app.candidate_id,
                Application.id != app.id,
                Application.stage.in_([
                    ApplicationStage.INTERVIEW,
                    ApplicationStage.OFFER,
                    ApplicationStage.HIRED,
                ]),
            )
        ).first()
        if in_progress:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该候选人已在其他申请流程中，请等待当前流程结束",
            )
    assert_application_transition(app.stage, target_stage)
    # 推进到 OFFER 需要有已完成评价的面试
    if target_stage == ApplicationStage.OFFER:
        from app.models import Interview, InterviewStatus

        completed = session.exec(
            select(Interview).where(
                Interview.application_id == app.id,
                Interview.status == InterviewStatus.COMPLETED,
            )
        ).first()
        if not completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先完成面试评价后再推进到 Offer 阶段",
            )
    # 重新进入面试阶段时，清理上一轮的 CANCELLED 面试
    if target_stage == ApplicationStage.INTERVIEW:
        from app.models import Interview, InterviewStatus

        cancelled = session.exec(
            select(Interview).where(
                Interview.application_id == app.id,
                Interview.status == InterviewStatus.CANCELLED,
            )
        ).all()
        for iv in cancelled:
            session.delete(iv)
        if cancelled:
            session.commit()
    # 离开 OFFER 阶段时，取消 DRAFT/PENDING 的 Offer
    if target_stage != ApplicationStage.OFFER and app.stage == ApplicationStage.OFFER:
        offer = session.exec(
            select(Offer).where(Offer.application_id == app.id)
        ).first()
        if offer and offer.status in (OfferStatus.DRAFT, OfferStatus.PENDING_APPROVAL):
            offer.status = OfferStatus.REJECTED
            session.add(offer)
    app.stage = target_stage
    session.add(app)
    session.commit()
    session.refresh(app)
    audit_service.log_action(
        session=session,
        user_id=user.id,
        action="advance",
        resource_type="application",
        resource_id=app.id,
        before=before,
        after={"stage": target_stage.value},
    )
    # Entering the OFFER stage auto-creates a draft offer (salary 0) so it
    # shows up in the Offers page; HR fills in the salary before submitting.
    # If a REJECTED offer already exists (e.g. after restore), reset it to DRAFT.
    if target_stage == ApplicationStage.OFFER:
        existing = session.exec(
            select(Offer).where(Offer.application_id == app.id)
        ).first()
        if existing and existing.status == OfferStatus.REJECTED:
            existing.status = OfferStatus.DRAFT
            existing.salary = 0
            existing.creator_id = user.id
            session.add(existing)
            session.commit()
        elif not existing:
            draft = Offer(
                application_id=app.id,
                salary=0,
                status=OfferStatus.DRAFT,
                creator_id=user.id,
            )
            session.add(draft)
            session.commit()
    # Notify the candidate of the stage change.
    cand_name, job_title, email = email_service.get_app_context(
        session=session, application_id=app.id
    )
    if email:
        email_service.send_stage_changed_email(
            email_to=email,
            recipient_name=cand_name,
            job_title=job_title,
            stage=target_stage,
        )
    return app


def reject_application(
    *, session: Session, user: User, application_id: uuid.UUID
) -> Application:
    app = get_application(session=session, user=user, application_id=application_id)
    assert_application_transition(app.stage, ApplicationStage.REJECTED)
    # 从 OFFER 淘汰时，取消 DRAFT/PENDING 的 Offer
    if app.stage == ApplicationStage.OFFER:
        offer = session.exec(
            select(Offer).where(Offer.application_id == app.id)
        ).first()
        if offer and offer.status in (OfferStatus.DRAFT, OfferStatus.PENDING_APPROVAL):
            offer.status = OfferStatus.REJECTED
            session.add(offer)
    # 淘汰时取消 SCHEDULED 面试，COMPLETED 面试标记为 REJECTED
    from app.models import Interview, InterviewStatus

    active = session.exec(
        select(Interview).where(
            Interview.application_id == app.id,
            Interview.status.in_([
                InterviewStatus.SCHEDULED,
                InterviewStatus.COMPLETED,
            ]),
        )
    ).all()
    for iv in active:
        if iv.status == InterviewStatus.SCHEDULED:
            iv.status = InterviewStatus.CANCELLED
        elif iv.status == InterviewStatus.COMPLETED:
            iv.status = InterviewStatus.REJECTED
        session.add(iv)
    app.stage = ApplicationStage.REJECTED
    session.add(app)
    session.commit()
    session.refresh(app)
    # Notify the candidate they were rejected.
    cand_name, job_title, email = email_service.get_app_context(
        session=session, application_id=app.id
    )
    if email:
        email_service.send_stage_changed_email(
            email_to=email,
            recipient_name=cand_name,
            job_title=job_title,
            stage=app.stage,
        )
    return app


def restore_application(
    *, session: Session, user: User, application_id: uuid.UUID
) -> Application:
    app = get_application(session=session, user=user, application_id=application_id)
    if app.stage != ApplicationStage.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only rejected applications can be restored",
        )
    # 同候选人+同职位有正在流程中的申请则不能恢复
    existing = session.exec(
        select(Application).where(
            Application.candidate_id == app.candidate_id,
            Application.job_id == app.job_id,
            Application.id != app.id,
            Application.stage != ApplicationStage.REJECTED,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该候选人对该职位已有正在流程中的申请，不能恢复",
        )
    assert_application_transition(app.stage, ApplicationStage.SCREENING)
    app.stage = ApplicationStage.SCREENING
    session.add(app)
    session.commit()
    session.refresh(app)
    return app


def batch_advance(
    *,
    session: Session,
    user: User,
    application_ids: list[uuid.UUID],
    target_stage: ApplicationStage,
) -> list[Application]:
    """Advance multiple applications to the same stage (best-effort)."""
    apps: list[Application] = []
    for app_id in application_ids:
        try:
            app = advance_application(
                session=session,
                user=user,
                application_id=app_id,
                target_stage=target_stage,
            )
            apps.append(app)
        except HTTPException:
            # Skip applications that can't transition (wrong stage / not found).
            continue
    return apps


def batch_notify(
    *,
    session: Session,
    user: User,
    notify_in: BatchNotify,
) -> BatchNotifyResult:
    """§16 batch notify: send an in-app message to each application's owner.

    Only applications visible to the caller (data scope) are considered.
    Applications without an assigned owner are skipped.
    """
    result = BatchNotifyResult()
    seen: set[uuid.UUID] = set()
    for app_id in notify_in.application_ids:
        if app_id in seen:
            continue
        seen.add(app_id)
        try:
            app = get_application(session=session, user=user, application_id=app_id)
        except HTTPException:
            continue
        if not app.owner_id:
            result.skipped += 1
            continue
        notification_service.create_notification(
            session=session,
            user_id=app.owner_id,
            type="batch_notify",
            content=notify_in.message,
            related_type="application",
            related_id=app.id,
        )
        result.notified += 1
    return result
