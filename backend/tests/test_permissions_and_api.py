from datetime import timedelta

from bson import ObjectId
from fastapi.testclient import TestClient

from app.api.v1.auth import get_auth_service
from app.api.v1.users import get_user_service
from app.core.constants import UserRoles, UserStatus
from app.core.permissions import get_current_user, get_user_repository_factory
from app.core.security import create_access_token
from app.main import app
from app.utils.datetime import utc_now


def make_user(role=UserRoles.ADMIN, status=UserStatus.ACTIVE):
    return {
        "_id": ObjectId(),
        "name": "Test User",
        "email": "test@example.com",
        "phone": None,
        "password_hash": "hidden",
        "role": role,
        "status": status,
        "last_login_at": utc_now(),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "created_by": None,
        "updated_by": None,
    }


class FakeAuthService:
    async def login(self, email, password, request_context):
        return {
            "access_token": "login-token",
            "token_type": "bearer",
            "user": {
                "id": str(ObjectId()),
                "name": "System Admin",
                "email": email,
                "role": "admin",
                "status": "active",
            },
        }

    def get_current_user_profile(self, user):
        return {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "role": user["role"],
            "status": user["status"],
            "last_login_at": user["last_login_at"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "created_by": None,
            "updated_by": None,
        }

    def refresh_access_token(self, user):
        return {"access_token": "fresh-token", "token_type": "bearer"}


class FakeUserService:
    async def create_guard(self, request_data, current_user, request_context):
        return {
            "id": str(ObjectId()),
            "name": request_data.name,
            "email": str(request_data.email),
            "phone": request_data.phone,
            "role": "guard",
            "status": "active",
            "created_at": utc_now(),
        }

    async def list_users(self, filters):
        return {
            "data": [],
            "pagination": {"page": filters["page"], "limit": filters["limit"], "total": 0, "pages": 0},
        }

    async def get_user_by_id(self, user_id):
        user = make_user(role=UserRoles.GUARD)
        return {
            "id": user_id,
            "name": user["name"],
            "email": user["email"],
            "phone": None,
            "role": "guard",
            "status": "active",
        }

    async def update_user(self, user_id, request_data, current_user, request_context):
        result = await self.get_user_by_id(user_id)
        result.update(request_data.model_dump(exclude_unset=True))
        return result

    async def delete_user(self, user_id, current_user, request_context):
        return {"id": user_id, "status": "deleted"}

    async def reset_password(self, user_id, new_password, current_user, request_context):
        return {"id": user_id}


def client_with_user(user=None):
    app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()
    if user is not None:
        app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app, raise_server_exceptions=False)


def teardown_function():
    app.dependency_overrides.clear()


def test_openapi_contains_every_phase_7_route() -> None:
    schema = app.openapi()
    expected = {
        ("/api/v1/health", "get"),
        ("/api/v1/health/database", "get"),
        ("/api/v1/auth/login", "post"),
        ("/api/v1/auth/me", "get"),
        ("/api/v1/auth/refresh", "post"),
        ("/api/v1/users", "post"),
        ("/api/v1/users", "get"),
        ("/api/v1/users/{user_id}", "get"),
        ("/api/v1/users/{user_id}", "put"),
        ("/api/v1/users/{user_id}", "delete"),
        ("/api/v1/users/{user_id}/reset-password", "post"),
    }

    assert all(method in schema["paths"][path] for path, method in expected)


def test_login_me_and_refresh_use_standard_success_envelope() -> None:
    admin = make_user()
    client = client_with_user(admin)

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@parkingmanagement.com", "password": "Admin@123"},
    )
    me = client.get("/api/v1/auth/me")
    refresh = client.post("/api/v1/auth/refresh")

    assert login.status_code == 200
    assert login.json()["message"] == "Login successful"
    assert me.json()["data"]["id"] == str(admin["_id"])
    assert "password_hash" not in me.text
    assert refresh.json()["data"]["access_token"] == "fresh-token"


def test_missing_invalid_and_expired_tokens_have_documented_errors() -> None:
    client = client_with_user()

    missing = client.get("/api/v1/auth/me")
    invalid = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}
    )
    expired_token = create_access_token(
        {"sub": str(ObjectId()), "role": "admin"},
        expires_delta=timedelta(seconds=-1),
    )
    expired = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert (missing.status_code, missing.json()["error_code"]) == (401, "UNAUTHORIZED")
    assert (invalid.status_code, invalid.json()["error_code"]) == (401, "TOKEN_INVALID")
    assert (expired.status_code, expired.json()["error_code"]) == (401, "TOKEN_EXPIRED")


def test_valid_token_loads_active_user_and_rejects_missing_or_inactive_user() -> None:
    active_user = make_user()
    token = create_access_token(
        {"sub": str(active_user["_id"]), "role": active_user["role"]}
    )

    class Repository:
        def __init__(self, result):
            self.result = result

        async def find_by_id(self, user_id):
            return self.result

    client = client_with_user()
    app.dependency_overrides[get_user_repository_factory] = lambda: (
        lambda: Repository(active_user)
    )
    active = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    app.dependency_overrides[get_user_repository_factory] = lambda: (
        lambda: Repository(None)
    )
    missing = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    inactive_user = {**active_user, "status": UserStatus.INACTIVE}
    app.dependency_overrides[get_user_repository_factory] = lambda: (
        lambda: Repository(inactive_user)
    )
    inactive = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert active.status_code == 200
    assert (missing.status_code, missing.json()["error_code"]) == (401, "UNAUTHORIZED")
    assert (inactive.status_code, inactive.json()["error_code"]) == (403, "USER_INACTIVE")


def test_token_without_required_role_claim_is_invalid() -> None:
    user = make_user()
    token = create_access_token({"sub": str(user["_id"])})
    client = client_with_user()

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["error_code"] == "TOKEN_INVALID"


def test_guard_gets_403_on_admin_user_routes() -> None:
    client = client_with_user(make_user(role=UserRoles.GUARD))

    response = client.get("/api/v1/users")

    assert response.status_code == 403
    assert response.json()["error_code"] == "FORBIDDEN"


def test_admin_can_use_all_user_routes() -> None:
    client = client_with_user(make_user())
    user_id = str(ObjectId())

    create = client.post(
        "/api/v1/users",
        json={
            "name": "Ali Guard",
            "email": "guard@example.com",
            "phone": "+923001234567",
            "password": "Guard@123",
            "role": "guard",
        },
    )
    listed = client.get("/api/v1/users?page=1&limit=20&role=guard&status=active")
    fetched = client.get(f"/api/v1/users/{user_id}")
    updated = client.put(f"/api/v1/users/{user_id}", json={"name": "Ali Khan"})
    reset = client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"new_password": "NewGuard@123"},
    )
    deleted = client.delete(f"/api/v1/users/{user_id}")

    assert [response.status_code for response in (create, listed, fetched, updated, reset, deleted)] == [201, 200, 200, 200, 200, 200]
    assert listed.json()["pagination"]["pages"] == 0
    assert deleted.json()["data"]["status"] == "deleted"
    assert all("password_hash" not in response.text for response in (create, listed, fetched, updated, reset, deleted))


def test_request_validation_uses_standard_error_envelope_without_password() -> None:
    client = client_with_user(make_user())

    response = client.post(
        "/api/v1/users",
        json={
            "name": "Bad",
            "email": "not-email",
            "password": "secret",
            "role": "admin",
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"
    assert "secret" not in response.text
