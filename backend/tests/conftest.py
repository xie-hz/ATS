import os

# Use a separate test database so pytest never wipes the dev DB.
# This must be set before importing anything from `app`.
os.environ.setdefault("POSTGRES_DB", "app_test")

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

import app.models  # noqa: F401  ensure models registered for metadata
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from tests.utils.user import create_user_with_role, get_engineering_department_id
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def _disable_real_email() -> Generator[None]:
    """Force-disable SMTP for the whole test session so tests never hit the
    real mail server configured in .env. Tests that exercise email logic
    re-enable SMTP per-test via monkeypatch on `settings.SMTP_HOST`.
    """
    original = settings.SMTP_HOST
    settings.SMTP_HOST = None
    yield
    settings.SMTP_HOST = original


class _FakeRedis:
    """In-memory stand-in for the Redis client (setex/get/delete) so portal
    auth tests don't require a running Redis."""

    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    def setex(self, name: str, time: int, value: str) -> None:
        self.store[name] = value

    def get(self, name: str) -> str | None:
        return self.store.get(name)

    def delete(self, name: str) -> int:
        return 1 if self.store.pop(name, None) is not None else 0


@pytest.fixture()
def fake_redis(monkeypatch) -> _FakeRedis:
    fake = _FakeRedis()
    # Patch at the call site: portal_service bound `get_redis` at import time,
    # so patching app.core.redis.get_redis wouldn't reach it.
    monkeypatch.setattr("app.services.portal_service.get_redis", lambda: fake)
    return fake


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session]:
    # Recreate schema in the test DB from the SQLModel metadata, then seed.
    # The dev DB (`app`) is never touched by tests.
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        init_db(session)
        yield session


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def hr_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    from tests.utils.user import user_authentication_headers

    user, password = create_user_with_role(db=db, role_code="hr")
    return user_authentication_headers(
        client=client, email=user.email, password=password
    )


@pytest.fixture(scope="module")
def hm_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    from tests.utils.user import user_authentication_headers

    dept = get_engineering_department_id(db)
    user, password = create_user_with_role(
        db=db, role_code="hiring_manager", department_id=dept.id if dept else None
    )
    return user_authentication_headers(
        client=client, email=user.email, password=password
    )


@pytest.fixture(scope="module")
def interviewer_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    from tests.utils.user import user_authentication_headers

    user, password = create_user_with_role(db=db, role_code="interviewer")
    return user_authentication_headers(
        client=client, email=user.email, password=password
    )
