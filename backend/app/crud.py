"""Pure data-access functions (no permissions, no business rules).

Permission checks and state-machine transitions live in `app.services`.
This module only holds atomic reads/writes shared by services and `init_db`.
"""

import uuid

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Department,
    Permission,
    Role,
    User,
    UserCreate,
    UserRole,
)

# ---------------------------------------------------------------------------
# User / auth
# ---------------------------------------------------------------------------


def get_user_by_email(*, session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()


def get_user(*, session: Session, user_id: uuid.UUID) -> User | None:
    return session.get(User, user_id)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


# Dummy hash to use for timing-attack prevention when the user is not found.
# Argon2 hash of a random password, used to ensure constant-time comparison.
DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$"
    "YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)
    if not user:
        # Prevent timing attacks by running verification even when the email
        # is unknown, so response time is similar whether or not it exists.
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        user.hashed_password = updated_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Role / permission
# ---------------------------------------------------------------------------


def get_role_by_code(*, session: Session, code: str) -> Role | None:
    stmt = select(Role).where(Role.code == code)
    return session.exec(stmt).first()


def get_permission_by_code(*, session: Session, code: str) -> Permission | None:
    stmt = select(Permission).where(Permission.code == code)
    return session.exec(stmt).first()


def assign_role(*, session: Session, user: User, role: Role) -> UserRole:
    link = UserRole(user_id=user.id, role_id=role.id)
    session.add(link)
    return link


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------


def get_department(*, session: Session, department_id: uuid.UUID) -> Department | None:
    return session.get(Department, department_id)
