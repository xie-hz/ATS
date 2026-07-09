from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"
TOKEN_TYPE_PORTAL = "portal"


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": token_type}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str | Any) -> str:
    return _create_token(
        str(subject),
        TOKEN_TYPE_ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str | Any) -> str:
    return _create_token(
        str(subject),
        TOKEN_TYPE_REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_portal_token(email: str) -> str:
    return _create_token(
        email,
        TOKEN_TYPE_PORTAL,
        timedelta(minutes=settings.PORTAL_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict:
    """Decode a JWT. Raises jwt.exceptions.InvalidTokenError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
