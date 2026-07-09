"""Admin authentication: login + refresh."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from app import crud
from app.api.deps import SessionDep
from app.core import security
from app.models import RefreshTokenRequest, Token

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login")
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return Token(
        access_token=security.create_access_token(user.id),
        refresh_token=security.create_refresh_token(user.id),
    )


@router.post("/refresh")
def refresh_token(body: RefreshTokenRequest) -> Token:
    try:
        payload = security.decode_token(body.refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from exc
    if payload.get("type") != security.TOKEN_TYPE_REFRESH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token type"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
        )
    return Token(
        access_token=security.create_access_token(user_id),
        refresh_token=security.create_refresh_token(user_id),
    )
