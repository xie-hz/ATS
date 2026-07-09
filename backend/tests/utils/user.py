from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.models import Department, User, UserCreate
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/admin/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_user_with_role(
    *, db: Session, role_code: str, department_id=None
) -> tuple[User, str]:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(
        email=email,
        password=password,
        name="Test User",
        department_id=department_id,
        role_codes=[role_code],
    )
    user = crud.create_user(session=db, user_create=user_in)
    role = crud.get_role_by_code(session=db, code=role_code)
    if role:
        crud.assign_role(session=db, user=user, role=role)
        db.commit()
        db.refresh(user)
    return user, password


def get_engineering_department_id(db: Session):
    stmt = select(Department).where(Department.name == "Engineering")
    return db.exec(stmt).first()
