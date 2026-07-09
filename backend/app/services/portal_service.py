"""Candidate portal service: public job browsing, applications, email-code auth.

Portal users authenticate via an email verification code (no password).
The code is stored in the DB; wiring it to a real SMTP sender is phase 2.
For now tests read the latest code from the DB directly.
"""

import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.core import security
from app.core.config import settings
from app.core.state_machines import assert_offer_transition
from app.models import (
    Application,
    ApplicationStage,
    Candidate,
    EmailVerificationCode,
    Job,
    JobPublic,
    JobsPublic,
    JobStatus,
    Offer,
    OfferPublic,
    OfferStatus,
    PortalApplicationPublic,
    PortalApplicationSubmit,
)
from app.services.base import not_found
from app.services.candidate_service import get_candidate_by_email
from app.utils import send_email


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
    return app


def send_verification_code(*, session: Session, email: str) -> None:
    code = "".join(secrets.choice("0123456789") for _ in range(6))
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES
    )
    record = EmailVerificationCode(email=email, code=code, expires_at=expires_at)
    session.add(record)
    session.commit()
    if settings.emails_enabled:
        html = (
            f"<p>Your verification code is: <strong>{code}</strong></p>"
            f"<p>It expires in "
            f"{settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES} minutes.</p>"
        )
        send_email(
            email_to=email,
            subject=f"{settings.PROJECT_NAME} - Verification Code",
            html_content=html,
        )


def verify_code(*, session: Session, email: str, code: str) -> str:
    record = session.exec(
        select(EmailVerificationCode)
        .where(
            EmailVerificationCode.email == email,
            EmailVerificationCode.code == code,
            EmailVerificationCode.used == False,  # noqa: E712
            EmailVerificationCode.expires_at >= datetime.now(UTC),
        )
        .order_by(col(EmailVerificationCode.created_at).desc())
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    record.used = True
    session.add(record)
    session.commit()
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
