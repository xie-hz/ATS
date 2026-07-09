"""Shared helpers for the service layer."""

from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.permissions import get_user_data_scope
from app.models import DataScopeType, User


def not_found(name: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{name} not found"
    )


def forbidden(detail: str = "Not enough permissions") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def get_scope(session: Session, user: User) -> DataScopeType:
    """Widest data scope across the user's roles."""
    return get_user_data_scope(session, user)
