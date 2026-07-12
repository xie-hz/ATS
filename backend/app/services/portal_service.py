"""Candidate portal service: public job browsing, applications, email-code auth.

Portal users authenticate via an email verification code (no password). The
code is stored in Redis with a short TTL (and deleted on use), so nothing
ephemeral piles up in the DB.
"""

import secrets
import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.core import security
from app.core.config import settings
from app.core.redis import get_redis
from app.core.state_machines import assert_offer_transition
from app.models import (
    Application,
    ApplicationStage,
    Candidate,
    Job,
    JobPublic,
    JobsPublic,
    JobStatus,
    Offer,
    OfferPublic,
    OfferStatus,
    PortalApplicationPublic,
    PortalApplicationSubmit,
    PortalProfileUpdate,
)
from app.services import email_service
from app.services.base import not_found
from app.services.candidate_service import get_candidate_by_email

# Redis key for a candidate's verification code: portal:code:<email>.
CODE_KEY = "portal:code:{}"


def list_portal_jobs(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    keyword: str | None = None,
) -> JobsPublic:
    stmt = select(Job).where(Job.status == JobStatus.OPEN)
    if keyword:
        stmt = stmt.where(col(Job.title).ilike(f"%{keyword}%"))
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(Job.created_at).desc()).offset(skip).limit(limit)
    jobs = session.exec(stmt).all()
    return JobsPublic(data=[JobPublic.model_validate(j) for j in jobs], count=count)


def get_portal_job(*, session: Session, job_id) -> Job:
    job = session.get(Job, job_id)
    if not job or job.status != JobStatus.OPEN:
        raise not_found("Job")
    return job


def submit_application(
    *, session: Session, submit_in: PortalApplicationSubmit
) -> Application:
    job = session.get(Job, submit_in.job_id)
    if not job or job.status != JobStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not open for applications",
        )
    # Reuse an existing candidate record when the email is already known.
    candidate = get_candidate_by_email(session=session, email=submit_in.email)
    if not candidate:
        candidate = Candidate(
            name=submit_in.name,
            email=submit_in.email,
            phone=submit_in.phone,
            source=submit_in.source or "portal",
            resume_url=submit_in.resume_url,
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
    else:
        # Keep the candidate record in sync: applying with edited info persists
        # name/phone/resume changes so future applications are pre-filled.
        changed = False
        if submit_in.name and submit_in.name != candidate.name:
            candidate.name = submit_in.name
            changed = True
        if submit_in.phone != candidate.phone:
            candidate.phone = submit_in.phone
            changed = True
        if submit_in.resume_url and submit_in.resume_url != candidate.resume_url:
            candidate.resume_url = submit_in.resume_url
            changed = True
        if changed:
            session.add(candidate)
            session.commit()
            session.refresh(candidate)
    # Block duplicate active applications for the same job.
    existing = session.exec(
        select(Application).where(
            Application.candidate_id == candidate.id,
            Application.job_id == job.id,
            Application.stage != ApplicationStage.REJECTED,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job",
        )
    app = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        stage=ApplicationStage.APPLIED,
        source=submit_in.source or "portal",
    )
    session.add(app)
    session.commit()
    session.refresh(app)
    # Notify the candidate their application was received.
    email_service.send_application_submitted_email(
        email_to=submit_in.email, recipient_name=candidate.name, job_title=job.title
    )
    return app


def send_verification_code(*, session: Session, email: str) -> None:
    code = "".join(secrets.choice("0123456789") for _ in range(6))
    ttl = settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES * 60
    # Store in Redis with a TTL: auto-expires, single latest code per email,
    # no rows accumulate in the DB.
    get_redis().setex(CODE_KEY.format(email), ttl, code)
    # Personalize with the candidate's name if we have a record for this email.
    candidate = get_candidate_by_email(session=session, email=email)
    email_service.send_verification_code_email(
        email_to=email,
        recipient_name=candidate.name if candidate else None,
        code=code,
        expire_minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES,
    )


def verify_code(*, email: str, code: str) -> str:
    stored = get_redis().get(CODE_KEY.format(email))
    if not stored or stored != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    # One-time use: delete immediately after a successful verify.
    get_redis().delete(CODE_KEY.format(email))
    return security.create_portal_token(email)


def list_portal_applications(
    *, session: Session, email: str
) -> list[PortalApplicationPublic]:
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        return []
    stmt = (
        select(Application, Job.title)
        .join(Job, Job.id == Application.job_id)
        .where(Application.candidate_id == candidate.id)
        .order_by(col(Application.created_at).desc())
    )
    rows = session.exec(stmt).all()
    return [
        PortalApplicationPublic(
            id=app.id,
            job_id=app.job_id,
            job_title=title,
            stage=app.stage,
            created_at=app.created_at,
        )
        for app, title in rows
    ]


def get_portal_application(
    *, session: Session, application_id: uuid.UUID, email: str
) -> PortalApplicationPublic:
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        raise not_found("Application")
    stmt = (
        select(Application, Job.title)
        .join(Job, Job.id == Application.job_id)
        .where(
            Application.id == application_id,
            Application.candidate_id == candidate.id,
        )
    )
    row = session.exec(stmt).first()
    if not row:
        raise not_found("Application")
    app, title = row
    return PortalApplicationPublic(
        id=app.id,
        job_id=app.job_id,
        job_title=title,
        stage=app.stage,
        created_at=app.created_at,
    )


def list_portal_offers(
    *, session: Session, email: str
) -> list[OfferPublic]:
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        return []
    stmt = (
        select(Offer)
        .join(Application, Application.id == Offer.application_id)
        .where(Application.candidate_id == candidate.id)
        .order_by(col(Offer.created_at).desc())
    )
    offers = session.exec(stmt).all()
    return [OfferPublic.model_validate(o) for o in offers]


def get_portal_offer(
    *, session: Session, offer_id: uuid.UUID, email: str
) -> Offer:
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        raise not_found("Offer")
    stmt = (
        select(Offer)
        .join(Application, Application.id == Offer.application_id)
        .where(Offer.id == offer_id, Application.candidate_id == candidate.id)
    )
    offer = session.exec(stmt).first()
    if not offer:
        raise not_found("Offer")
    return offer


def accept_portal_offer(
    *, session: Session, offer_id: uuid.UUID, email: str
) -> Offer:
    offer = get_portal_offer(session=session, offer_id=offer_id, email=email)
    assert_offer_transition(offer.status, OfferStatus.ACCEPTED)
    offer.status = OfferStatus.ACCEPTED
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def reject_portal_offer(
    *, session: Session, offer_id: uuid.UUID, email: str
) -> Offer:
    offer = get_portal_offer(session=session, offer_id=offer_id, email=email)
    assert_offer_transition(offer.status, OfferStatus.REJECTED)
    offer.status = OfferStatus.REJECTED
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def get_portal_profile(*, session: Session, email: str) -> Candidate:
    """Return the candidate's own profile. 404 if they have no record yet."""
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        raise not_found("Profile")
    return candidate


def update_portal_profile(
    *, session: Session, email: str, profile_in: PortalProfileUpdate
) -> Candidate:
    """Update editable profile fields (name/phone). Email is read-only."""
    candidate = get_candidate_by_email(session=session, email=email)
    if not candidate:
        raise not_found("Profile")
    candidate.name = profile_in.name
    candidate.phone = profile_in.phone
    session.add(candidate)
    session.commit()
    session.refresh(candidate)
    return candidate
