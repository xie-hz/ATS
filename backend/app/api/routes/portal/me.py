"""Portal profile: the candidate views / edits their own info (portal token)."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.deps import SessionDep, get_current_portal_email
from app.models import PortalProfile, PortalProfileUpdate
from app.services import portal_service

router = APIRouter(prefix="/portal/me", tags=["portal-profile"])


@router.get("/", response_model=PortalProfile)
def get_my_profile(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
) -> Any:
    candidate = portal_service.get_portal_profile(session=session, email=email)
    return PortalProfile.model_validate(candidate)


@router.patch("/", response_model=PortalProfile)
def update_my_profile(
    session: SessionDep,
    email: Annotated[str, Depends(get_current_portal_email)],
    profile_in: PortalProfileUpdate,
) -> Any:
    candidate = portal_service.update_portal_profile(
        session=session, email=email, profile_in=profile_in
    )
    return PortalProfile.model_validate(candidate)
