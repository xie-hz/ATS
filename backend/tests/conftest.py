import os

# Use a separate test database so pytest never wipes the dev DB.
# This must be set before importing anything from `app`.
os.environ.setdefault("POSTGRES_DB", "app_test")

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

import app.models  # noqa: F401  ensure models registered for metadata
from app.core.db import engine, init_db
from app.main import app
from tests.utils.user import create_user_with_role, get_engineering_department_id
from tests.utils.utils import get_superuser_token_headers


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
