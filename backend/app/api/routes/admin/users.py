"""Admin user management + self-service endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, SessionDep, get_current_user, require_permission
from app.core.permissions import Permissions
from app.models import (
    Message,
    UpdatePassword,
    UserCreate,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


# --- self-service (any authenticated internal user) ---


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser, session: SessionDep) -> Any:
    return user_service.to_public(session, current_user)


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
) -> Any:
    user = user_service.update_me(
        session=session, current_user=current_user, user_in=user_in
    )
    return user_service.to_public(session, user)


@router.patch("/me/password", response_model=Message)
def update_password_me(
    session: SessionDep,
    current_user: CurrentUser,
    body: UpdatePassword,
) -> Any:
    user_service.update_password_me(
        session=session, current_user=current_user, body=body
    )
    return Message(message="Password updated successfully")


# --- admin user management ---


@router.get(
    "/",
    response_model=UsersPublic,
    dependencies=[Depends(get_current_user)],
)
def list_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    return user_service.list_users(session=session, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=UserPublic,
    dependencies=[Depends(require_permission(Permissions.USER_MANAGE))],
)
def create_user(
    session: SessionDep,
    user_in: UserCreate,
) -> Any:
    user = user_service.create_user(session=session, user_in=user_in)
    return user_service.to_public(session, user)


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(require_permission(Permissions.USER_MANAGE))],
)
def get_user(
    session: SessionDep,
    user_id: uuid.UUID,
) -> Any:
    user = user_service.get_user(session=session, user_id=user_id)
    return user_service.to_public(session, user)


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
    dependencies=[Depends(require_permission(Permissions.USER_MANAGE))],
)
def update_user(
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    user = user_service.update_user(
        session=session, user_id=user_id, user_in=user_in
    )
    return user_service.to_public(session, user)
