"""Offer service: offer status machine (draft -> approval -> sent)."""

import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select

from app.core.state_machines import assert_offer_transition
from app.models import (
    Application,
    DataScopeType,
    Interview,
    Job,
    Offer,
    OfferCreate,
    OfferPublic,
    OffersPublic,
    OfferStatus,
    User,
)
from app.services import audit_service, email_service
from app.services.base import get_scope, not_found


def _scoped(session: Session, user: User):
    stmt = select(Offer)
    scope = get_scope(session, user)
    if scope == DataScopeType.DEPARTMENT:
        stmt = (
            stmt.join(Application, Application.id == Offer.application_id)
            .join(Job, Job.id == Application.job_id)
            .where(Job.department_id == user.department_id)
        )
    elif scope == DataScopeType.SELF:
        stmt = (
            stmt.join(Application, Application.id == Offer.application_id)
            .join(Interview, Interview.application_id == Application.id)
            .where(Interview.interviewer_id == user.id)
            .distinct()
        )
    return stmt


def list_offers(
    *, session: Session, user: User, skip: int = 0, limit: int = 100
) -> OffersPublic:
    stmt = _scoped(session, user)
    count = session.exec(select(func.count()).select_from(stmt.subquery())).one()
    stmt = stmt.order_by(col(Offer.created_at).desc()).offset(skip).limit(limit)
    offers = session.exec(stmt).all()
    return OffersPublic(
        data=[OfferPublic.model_validate(o) for o in offers], count=count
    )


def get_offer(*, session: Session, user: User, offer_id: uuid.UUID) -> Offer:
    stmt = _scoped(session, user).where(Offer.id == offer_id)
    offer = session.exec(stmt).first()
    if not offer:
        raise not_found("Offer")
    return offer


def update_offer(
    *, session: Session, user: User, offer_id: uuid.UUID, salary: int
) -> Offer:
    offer = get_offer(session=session, user=user, offer_id=offer_id)
    offer.salary = salary
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def create_offer(
    *, session: Session, user: User, offer_in: OfferCreate
) -> Offer:
    app = session.get(Application, offer_in.application_id)
    if not app:
        raise not_found("Application")
    existing = session.exec(
        select(Offer).where(Offer.application_id == app.id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offer already exists for this application",
        )
    offer = Offer.model_validate(
        offer_in,
        update={"status": OfferStatus.DRAFT, "creator_id": user.id},
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def submit_offer(*, session: Session, user: User, offer_id: uuid.UUID) -> Offer:
    offer = get_offer(session=session, user=user, offer_id=offer_id)
    before = {"status": offer.status.value}
    assert_offer_transition(offer.status, OfferStatus.PENDING_APPROVAL)
    offer.status = OfferStatus.PENDING_APPROVAL
    session.add(offer)
    session.commit()
    session.refresh(offer)
    audit_service.log_action(
        session=session,
        user_id=user.id,
        action="offer_submit",
        resource_type="offer",
        resource_id=offer.id,
        before=before,
        after={"status": OfferStatus.PENDING_APPROVAL.value},
    )
    return offer


def approve_offer(*, session: Session, user: User, offer_id: uuid.UUID) -> Offer:
    offer = get_offer(session=session, user=user, offer_id=offer_id)
    before = {"status": offer.status.value}
    assert_offer_transition(offer.status, OfferStatus.APPROVED)
    offer.status = OfferStatus.APPROVED
    offer.approved_by = user.id
    session.add(offer)
    session.commit()
    session.refresh(offer)
    audit_service.log_action(
        session=session,
        user_id=user.id,
        action="offer_approve",
        resource_type="offer",
        resource_id=offer.id,
        before=before,
        after={"status": OfferStatus.APPROVED.value},
    )
    return offer


def send_offer(*, session: Session, user: User, offer_id: uuid.UUID) -> Offer:
    offer = get_offer(session=session, user=user, offer_id=offer_id)
    before = {"status": offer.status.value}
    assert_offer_transition(offer.status, OfferStatus.SENT)
    offer.status = OfferStatus.SENT
    session.add(offer)
    session.commit()
    session.refresh(offer)
    audit_service.log_action(
        session=session,
        user_id=user.id,
        action="offer_send",
        resource_type="offer",
        resource_id=offer.id,
        before=before,
        after={"status": OfferStatus.SENT.value},
    )
    # Notify the candidate their offer has been sent.
    cand_name, job_title, email = email_service.get_app_context(
        session=session, application_id=offer.application_id
    )
    if email:
        email_service.send_offer_email(
            email_to=email,
            recipient_name=cand_name,
            job_title=job_title,
            salary=offer.salary,
        )
    return offer


def cancel_offer(*, session: Session, user: User, offer_id: uuid.UUID) -> Offer:
    """HR cancels an offer (DRAFT/PENDING/APPROVED -> REJECTED)."""
    offer = get_offer(session=session, user=user, offer_id=offer_id)
    assert_offer_transition(offer.status, OfferStatus.REJECTED)
    offer.status = OfferStatus.REJECTED
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer
