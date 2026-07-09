"""Admin offer management: create + submit/approve/send flow."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, require_permission
from app.core.permissions import Permissions
from app.models import OfferCreate, OfferPublic, OffersPublic, OfferUpdate, User
from app.services import offer_service

router = APIRouter(prefix="/admin/offers", tags=["admin-offers"])


@router.get("/", response_model=OffersPublic)
def list_offers(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_READ))],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return offer_service.list_offers(
        session=session, user=current_user, skip=skip, limit=limit
    )


@router.post("/", response_model=OfferPublic)
def create_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_CREATE))],
    offer_in: OfferCreate,
) -> Any:
    offer = offer_service.create_offer(
        session=session, user=current_user, offer_in=offer_in
    )
    return OfferPublic.model_validate(offer)


@router.get("/{offer_id}", response_model=OfferPublic)
def get_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_READ))],
    offer_id: uuid.UUID,
) -> Any:
    offer = offer_service.get_offer(
        session=session, user=current_user, offer_id=offer_id
    )
    return OfferPublic.model_validate(offer)


@router.patch("/{offer_id}", response_model=OfferPublic)
def update_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_CREATE))],
    offer_id: uuid.UUID,
    body: OfferUpdate,
) -> Any:
    """Update offer salary (e.g. fill in a draft offer before submitting)."""
    offer = offer_service.update_offer(
        session=session, user=current_user, offer_id=offer_id, salary=body.salary
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/submit", response_model=OfferPublic)
def submit_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_SUBMIT))],
    offer_id: uuid.UUID,
) -> Any:
    offer = offer_service.submit_offer(
        session=session, user=current_user, offer_id=offer_id
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/approve", response_model=OfferPublic)
def approve_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_APPROVE))],
    offer_id: uuid.UUID,
) -> Any:
    offer = offer_service.approve_offer(
        session=session, user=current_user, offer_id=offer_id
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/send", response_model=OfferPublic)
def send_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_SEND))],
    offer_id: uuid.UUID,
) -> Any:
    offer = offer_service.send_offer(
        session=session, user=current_user, offer_id=offer_id
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/cancel", response_model=OfferPublic)
def cancel_offer(
    session: SessionDep,
    current_user: Annotated[User, Depends(require_permission(Permissions.OFFER_CREATE))],
    offer_id: uuid.UUID,
) -> Any:
    """HR cancels an offer (DRAFT/PENDING/APPROVED -> REJECTED)."""
    offer = offer_service.cancel_offer(
        session=session, user=current_user, offer_id=offer_id
    )
    return OfferPublic.model_validate(offer)
