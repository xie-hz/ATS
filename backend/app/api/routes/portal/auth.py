"""Portal email-code authentication (no password)."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.models import Message, PortalToken, SendCodeRequest, VerifyCodeRequest
from app.services import portal_service

router = APIRouter(prefix="/portal/auth", tags=["portal-auth"])


@router.post("/send-code", response_model=Message)
def send_code(session: SessionDep, body: SendCodeRequest) -> Any:
    portal_service.send_verification_code(session=session, email=body.email)
    return Message(
        message="If the email is registered, a verification code has been sent"
    )


@router.post("/verify", response_model=PortalToken)
def verify_code(session: SessionDep, body: VerifyCodeRequest) -> Any:
    token = portal_service.verify_code(
        session=session, email=body.email, code=body.code
    )
    return PortalToken(access_token=token)
