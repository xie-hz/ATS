"""Job service: data-scope filtering + job status machine."""

import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.core.state_machines import assert_job_transition
from app.models import (
    Application,
    DataScopeType,
    Interview,
    Job,
    JobCreate,
    JobPublic,
    JobsPublic,
    JobStatus,
    JobUpdate,
    User,
)
from app.services.base import get_scope, not_found


def _scoped(session: Session, user: User):
    stmt = select(Job)
    scope = get_scope(session, user)
    if scope == DataScopeType.DEPARTMENT:
        stmt = stmt.where(Job.department_id == user.department_id)
    elif scope == DataScopeType.SELF:
        # Interviewers see jobs they've been assigned to interview.
        stmt = (
            stmt.join(Application, Application.job_id == Job.id)
            .join(Interview, Interview.application_id == Application.id)
            .where(Interview.interviewer_id == user.id)
        )
    return stmt


def list_jobs(
    *,
    session: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
    job_status: JobStatus | None = None,
) -> JobsPublic:
    stmt = _scoped(session, user)
    if keyword:
        stmt = stmt.where(col(Job.title).ilike(f"%{keyword}%"))
    if job_status:
        stmt = stmt.where(Job.status == job_status)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(Job.created_at).desc()).offset(skip).limit(limit)
    jobs = session.exec(stmt).all()
    return JobsPublic(data=[JobPublic.model_validate(j) for j in jobs], count=count)


def get_job(*, session: Session, user: User, job_id: uuid.UUID) -> Job:
    stmt = _scoped(session, user).where(Job.id == job_id)
    job = session.exec(stmt).first()
    if not job:
        raise not_found("Job")
    return job


def create_job(*, session: Session, user: User, job_in: JobCreate) -> Job:
    job = Job.model_validate(
        job_in, update={"creator_id": user.id, "status": JobStatus.DRAFT}
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def update_job(
    *, session: Session, user: User, job_id: uuid.UUID, job_in: JobUpdate
) -> Job:
    job = get_job(session=session, user=user, job_id=job_id)
    job.sqlmodel_update(job_in.model_dump(exclude_unset=True))
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def publish_job(*, session: Session, user: User, job_id: uuid.UUID) -> Job:
    """Advance the job along its publication flow.

    DRAFT -> PENDING_APPROVAL -> OPEN.
    """
    job = get_job(session=session, user=user, job_id=job_id)
    if job.status == JobStatus.DRAFT:
        target = JobStatus.PENDING_APPROVAL
    elif job.status == JobStatus.PENDING_APPROVAL:
        target = JobStatus.OPEN
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish job in {job.status.value} state",
        )
    assert_job_transition(job.status, target)
    job.status = target
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def close_job(*, session: Session, user: User, job_id: uuid.UUID) -> Job:
    job = get_job(session=session, user=user, job_id=job_id)
    assert_job_transition(job.status, JobStatus.CLOSED)
    job.status = JobStatus.CLOSED
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def reopen_job(*, session: Session, user: User, job_id: uuid.UUID) -> Job:
    job = get_job(session=session, user=user, job_id=job_id)
    assert_job_transition(job.status, JobStatus.DRAFT)
    job.status = JobStatus.DRAFT
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def delete_job(*, session: Session, user: User, job_id: uuid.UUID) -> None:
    job = get_job(session=session, user=user, job_id=job_id)
    # 有申请的职位不能删
    apps = session.exec(
        select(Application).where(Application.job_id == job_id)
    ).first()
    if apps:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该职位有申请记录，请先关闭",
        )
    session.delete(job)
    session.commit()
