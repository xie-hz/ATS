from fastapi.testclient import TestClient

from app.core.config import settings


def test_login_admin(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/admin/auth/login", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient) -> None:
    login_data = {"username": settings.FIRST_SUPERUSER, "password": "wrong"}
    r = client.post(f"{settings.API_V1_STR}/admin/auth/login", data=login_data)
    assert r.status_code == 400


def test_refresh_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/admin/auth/login", data=login_data)
    refresh = r.json()["refresh_token"]
    r2 = client.post(
        f"{settings.API_V1_STR}/admin/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_refresh_token_rejects_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/admin/auth/login", data=login_data)
    access = r.json()["access_token"]
    r2 = client.post(
        f"{settings.API_V1_STR}/admin/auth/refresh",
        json={"refresh_token": access},
    )
    assert r2.status_code == 403


def test_read_me(client: TestClient, admin_token_headers: dict[str, str]) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admin/users/me", headers=admin_token_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert "email" in body
    assert "admin" in body["roles"]


def test_invalid_access_token(client: TestClient) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admin/users/me",
        headers={"Authorization": "Bearer invalid"},
    )
    assert r.status_code == 401
