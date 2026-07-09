"""Candidate service: data-scope filtering across application/interview joins."""

import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.models import (
    Application,
    Candidate,
    CandidateCreate,
    CandidatePublic,
    CandidatesPublic,
    CandidateUpdate,
    DataScopeType,
    Interview,
    Job,
    User,
)
from app.services.base import get_scope, not_found


def _scoped(session: Session, user: User):
    """Candidate query restricted by the caller's data scope.

    - ALL: no filter
    - DEPARTMENT: candidates who applied to a job in the user's department
    - SELF: candidates the user has been assigned to interview
    """
    stmt = select(Candidate)
    scope = get_scope(session, user)
    if scope == DataScopeType.DEPARTMENT:
        stmt = (
            stmt.join(Application, Application.candidate_id == Candidate.id)
            .join(Job, Job.id == Application.job_id)
            .where(Job.department_id == user.department_id)
        )
    elif scope == DataScopeType.SELF:
        stmt = (
            stmt.join(Application, Application.candidate_id == Candidate.id)
            .join(Interview, Interview.application_id == Application.id)
            .where(Interview.interviewer_id == user.id)
        )
    return stmt.distinct()


def list_candidates(
    *,
    session: Session,
    user: User,
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
    tag: str | None = None,
    source: str | None = None,
) -> CandidatesPublic:
    stmt = _scoped(session, user)
    if keyword:
        stmt = stmt.where(
            col(Candidate.name).ilike(f"%{keyword}%")
            | col(Candidate.email).ilike(f"%{keyword}%")
        )
    if tag:
        # JSONB containment: tags @> '["tag"]'
        stmt = stmt.where(Candidate.tags.contains([tag]))  # type: ignore
    if source:
        stmt = stmt.where(Candidate.source == source)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(Candidate.created_at).desc()).offset(skip).limit(limit)
    candidates = session.exec(stmt).all()
    return CandidatesPublic(
        data=[CandidatePublic.model_validate(c) for c in candidates], count=count
    )


def get_candidate(
    *, session: Session, user: User, candidate_id: uuid.UUID
) -> Candidate:
    stmt = _scoped(session, user).where(Candidate.id == candidate_id)
    candidate = session.exec(stmt).first()
    if not candidate:
        raise not_found("Candidate")
    return candidate


def get_candidate_by_email(
    *, session: Session, email: str
) -> Candidate | None:
    stmt = select(Candidate).where(Candidate.email == email)
    return session.exec(stmt).first()


def create_candidate(
    *, session: Session, candidate_in: CandidateCreate
) -> Candidate:
    if get_candidate_by_email(session=session, email=candidate_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在，请勿重复创建候选人",
        )
    candidate = Candidate.model_validate(candidate_in)
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate


def update_candidate(
    *,
    session: Session,
    user: User,
    candidate_id: uuid.UUID,
    candidate_in: CandidateUpdate,
) -> Candidate:
    candidate = get_candidate(session=session, user=user, candidate_id=candidate_id)
    candidate.sqlmodel_update(candidate_in.model_dump(exclude_unset=True))
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate


def set_resume_url(
    *, session: Session, user: User, candidate_id: uuid.UUID, resume_url: str
) -> Candidate:
    candidate = get_candidate(session=session, user=user, candidate_id=candidate_id)
    candidate.resume_url = resume_url
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate
