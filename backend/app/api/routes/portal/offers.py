"""Portal offers: candidates view / accept / reject their own offers."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_portal_email
from app.models import OfferPublic
from app.services import portal_service

router = APIRouter(prefix="/portal/offers", tags=["portal-offers"])


@router.get("/", response_model=list[OfferPublic])
def list_my_offers(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
) -> Any:
    return portal_service.list_portal_offers(session=session, email=email)


@router.get("/{offer_id}", response_model=OfferPublic)
def get_my_offer(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
    offer_id: uuid.UUID,
) -> Any:
    offer = portal_service.get_portal_offer(
        session=session, offer_id=offer_id, email=email
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/accept", response_model=OfferPublic)
def accept_offer(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
    offer_id: uuid.UUID,
) -> Any:
    offer = portal_service.accept_portal_offer(
        session=session, offer_id=offer_id, email=email
    )
    return OfferPublic.model_validate(offer)


@router.post("/{offer_id}/reject", response_model=OfferPublic)
def reject_offer(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
    offer_id: uuid.UUID,
) -> Any:
    offer = portal_service.reject_portal_offer(
        session=session, offer_id=offer_id, email=email
    )
    return OfferPublic.model_validate(offer)
