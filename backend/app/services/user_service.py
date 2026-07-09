"""User service: admin user management with role synchronization."""

import uuid

from fastapi import HTTPException, status
from sqlmodel import Session, col, delete, func, select

from app import crud
from app.core.permissions import get_user_role_codes
from app.core.security import get_password_hash, verify_password
from app.models import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRole,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.base import not_found


def to_public(session: Session, user: User) -> UserPublic:
    roles = get_user_role_codes(session, user)
    return UserPublic.model_validate(user, update={"roles": roles})


def _sync_roles(session: Session, user: User, role_codes: list[str]) -> None:
    session.exec(delete(UserRole).where(UserRole.user_id == user.id))
    for code in role_codes:
        role = crud.get_role_by_code(session=session, code=code)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown role: {code}",
            )
        session.add(UserRole(user_id=user.id, role_id=role.id))


def list_users(*, session: Session, skip: int = 0, limit: int = 100) -> UsersPublic:
    count = session.exec(select(func.count()).select_from(User)).one()
    stmt = select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    users = session.exec(stmt).all()
    return UsersPublic(
        data=[to_public(session, u) for u in users], count=count
    )


def get_user(*, session: Session, user_id: uuid.UUID) -> User:
    user = session.get(User, user_id)
    if not user:
        raise not_found("User")
    return user


def create_user(*, session: Session, user_in: UserCreate) -> User:
    if crud.get_user_by_email(session=session, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists",
        )
    user = crud.create_user(session=session, user_create=user_in)
    _sync_roles(session, user, user_in.role_codes)
    session.commit()
    session.refresh(user)
    return user


def update_user(
    *, session: Session, user_id: uuid.UUID, user_in: UserUpdate
) -> User:
    user = get_user(session=session, user_id=user_id)
    if user_in.email:
        existing = crud.get_user_by_email(session=session, email=user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
    data = user_in.model_dump(exclude_unset=True, exclude={"role_codes"})
    user.sqlmodel_update(data)
    session.add(user)
    if user_in.role_codes is not None:
        _sync_roles(session, user, user_in.role_codes)
    session.commit()
    session.refresh(user)
    return user


def update_me(
    *, session: Session, current_user: User, user_in: UserUpdateMe
) -> User:
    if user_in.email:
        existing = crud.get_user_by_email(session=session, email=user_in.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
    current_user.sqlmodel_update(user_in.model_dump(exclude_unset=True))
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def update_password_me(
    *, session: Session, current_user: User, body: UpdatePassword
) -> None:
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
        )
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )
    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    session.commit()
