from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from app.core.constants import AuditActions, UserRoles, UserStatus
from app.core.security import hash_password, verify_password
from app.schemas.common import AppException
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.services.audit_log_service import AuditLogService
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.datetime import utc_now


def make_user(**overrides):
    user = {
        "_id": ObjectId(),
        "name": "System Admin",
        "email": "admin@parkingmanagement.com",
        "phone": None,
        "password_hash": hash_password("Admin@123"),
        "role": UserRoles.ADMIN,
        "status": UserStatus.ACTIVE,
        "last_login_at": None,
        "created_by": None,
        "updated_by": None,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    user.update(overrides)
    return user


@pytest.mark.asyncio
async def test_audit_service_builds_safe_append_only_log() -> None:
    repository = AsyncMock()
    service = AuditLogService(repository)
    user = make_user()

    await service.log_action(
        user=user,
        action=AuditActions.USER_LOGIN_FAILED,
        entity="user",
        entity_id=user["_id"],
        message="Login failed",
        metadata={"email": user["email"], "password": "secret", "nested": {"access_token": "x"}},
        request_context={"ip_address": "127.0.0.1", "user_agent": "pytest"},
    )

    log = repository.create_log.await_args.args[0]
    assert log["user_id"] == user["_id"]
    assert log["user_role"] == UserRoles.ADMIN
    assert log["metadata"] == {"email": user["email"], "nested": {}}
    assert log["ip_address"] == "127.0.0.1"


@pytest.mark.asyncio
async def test_auth_login_returns_token_updates_login_and_audits() -> None:
    user = make_user()
    user_repository = AsyncMock()
    user_repository.find_by_email.return_value = user
    user_repository.update_last_login.return_value = {
        **user,
        "last_login_at": utc_now(),
    }
    audit_service = AsyncMock()
    service = AuthService(user_repository, audit_service)

    result = await service.login(
        user["email"],
        "Admin@123",
        {"ip_address": "127.0.0.1", "user_agent": "pytest"},
    )

    assert result["token_type"] == "bearer"
    assert result["user"]["id"] == str(user["_id"])
    assert "password_hash" not in result["user"]
    user_repository.update_last_login.assert_awaited_once_with(str(user["_id"]))
    assert audit_service.log_action.await_args.kwargs["action"] == AuditActions.USER_LOGIN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("user", "password", "status_code", "error_code"),
    [
        (None, "Admin@123", 401, "INVALID_CREDENTIALS"),
        (make_user(), "wrong-password", 401, "INVALID_CREDENTIALS"),
        (make_user(status=UserStatus.INACTIVE), "Admin@123", 403, "USER_INACTIVE"),
        (make_user(status=UserStatus.DELETED), "Admin@123", 403, "USER_INACTIVE"),
    ],
)
async def test_auth_login_rejects_failures_and_audits(
    user, password, status_code, error_code
) -> None:
    user_repository = AsyncMock()
    user_repository.find_by_email.return_value = user
    audit_service = AsyncMock()
    service = AuthService(user_repository, audit_service)

    with pytest.raises(AppException) as caught:
        await service.login("admin@parkingmanagement.com", password, {})

    assert caught.value.status_code == status_code
    assert caught.value.error_code == error_code
    assert (
        audit_service.log_action.await_args.kwargs["action"]
        == AuditActions.USER_LOGIN_FAILED
    )


@pytest.mark.asyncio
async def test_user_service_creates_guard_with_hash_and_audit() -> None:
    admin = make_user()
    repository = AsyncMock()
    repository.find_by_email.return_value = None
    repository.create_user.side_effect = lambda data: {"_id": ObjectId(), **data}
    audit_service = AsyncMock()
    service = UserService(repository, audit_service)
    request = UserCreateRequest(
        name="Ali Guard",
        email="guard@example.com",
        phone="+923001234567",
        password="Guard@123",
        role="guard",
    )

    result = await service.create_guard(request, admin, {})

    inserted = repository.create_user.await_args.args[0]
    assert verify_password("Guard@123", inserted["password_hash"])
    assert inserted["role"] == UserRoles.GUARD
    assert inserted["created_by"] == admin["_id"]
    assert "password_hash" not in result
    assert audit_service.log_action.await_args.kwargs["action"] == AuditActions.USER_CREATED


@pytest.mark.asyncio
async def test_user_service_rejects_duplicate_and_invalid_or_missing_ids() -> None:
    repository = AsyncMock()
    repository.find_by_email.return_value = make_user()
    service = UserService(repository, AsyncMock())
    request = UserCreateRequest(
        name="Ali",
        email="admin@parkingmanagement.com",
        password="Guard@123",
        role="guard",
    )

    with pytest.raises(AppException) as duplicate:
        await service.create_guard(request, make_user(), {})
    with pytest.raises(AppException) as invalid:
        await service.get_user_by_id("invalid")

    repository.find_by_id.return_value = None
    with pytest.raises(AppException) as missing:
        await service.get_user_by_id(str(ObjectId()))

    assert duplicate.value.status_code == 409
    assert invalid.value.status_code == 400
    assert missing.value.status_code == 404


@pytest.mark.asyncio
async def test_user_service_lists_updates_deletes_and_resets_password() -> None:
    admin = make_user()
    guard = make_user(
        _id=ObjectId(),
        email="guard@example.com",
        role=UserRoles.GUARD,
    )
    repository = AsyncMock()
    repository.list_users.return_value = [guard]
    repository.count_users.return_value = 1
    repository.find_by_id.return_value = guard
    repository.update_user.side_effect = lambda _id, data: {**guard, **data}
    repository.soft_delete_user.return_value = {
        **guard,
        "status": UserStatus.DELETED,
    }
    repository.update_password.return_value = guard
    audit_service = AsyncMock()
    service = UserService(repository, audit_service)

    listed = await service.list_users(
        {"page": 1, "limit": 20, "role": "guard", "status": "active", "search": "ali"}
    )
    updated = await service.update_user(
        str(guard["_id"]),
        UserUpdateRequest(name="Ali Khan"),
        admin,
        {},
    )
    deleted = await service.delete_user(str(guard["_id"]), admin, {})
    reset = await service.reset_password(
        str(guard["_id"]), "NewGuard@123", admin, {}
    )

    assert listed["pagination"]["total"] == 1
    assert "password_hash" not in listed["data"][0]
    assert updated["name"] == "Ali Khan"
    assert deleted["status"] == UserStatus.DELETED
    assert reset == {"id": str(guard["_id"])}
    password_hash = repository.update_password.await_args.args[1]
    assert verify_password("NewGuard@123", password_hash)


@pytest.mark.asyncio
async def test_user_service_prevents_self_delete() -> None:
    admin = make_user()
    repository = AsyncMock()
    repository.find_by_id.return_value = admin
    service = UserService(repository, AsyncMock())

    with pytest.raises(AppException) as caught:
        await service.delete_user(str(admin["_id"]), admin, {})

    assert caught.value.status_code == 403
    repository.soft_delete_user.assert_not_awaited()
