import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest
from app.schemas.common import AppException, ErrorResponse, PaginatedResponse
from app.schemas.user import (
    PasswordResetRequest,
    UserCreateRequest,
    UserUpdateRequest,
)


def test_login_requires_valid_email_and_eight_character_password() -> None:
    request = LoginRequest(email="ADMIN@parkingmanagement.com", password="Admin@123")

    assert str(request.email) == "admin@parkingmanagement.com"

    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="Admin@123")
    with pytest.raises(ValidationError):
        LoginRequest(email="admin@example.com", password="short")


def test_create_user_accepts_only_guard_and_strips_name() -> None:
    request = UserCreateRequest(
        name="  Ali Guard  ",
        email="GUARD@example.com",
        password="Guard@123",
        role="guard",
    )

    assert request.name == "Ali Guard"
    assert str(request.email) == "guard@example.com"

    with pytest.raises(ValidationError):
        UserCreateRequest(
            name="Admin",
            email="other@example.com",
            password="Admin@123",
            role="admin",
        )


def test_update_user_forbids_email_role_and_password() -> None:
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"email": "new@example.com"})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"role": "admin"})
    with pytest.raises(ValidationError):
        UserUpdateRequest.model_validate({"password": "Admin@123"})


def test_update_requires_at_least_one_allowed_field() -> None:
    with pytest.raises(ValidationError):
        UserUpdateRequest()


def test_password_reset_requires_eight_characters() -> None:
    assert PasswordResetRequest(new_password="NewGuard@123").new_password == "NewGuard@123"

    with pytest.raises(ValidationError):
        PasswordResetRequest(new_password="short")


def test_common_response_and_application_error_shapes() -> None:
    response = PaginatedResponse(
        message="Users fetched successfully",
        data=[],
        pagination={"page": 1, "limit": 20, "total": 0, "pages": 0},
    )
    error = AppException(
        status_code=404,
        message="User not found",
        error_code="USER_NOT_FOUND",
    )

    assert response.success is True
    assert response.pagination.pages == 0
    assert error.status_code == 404
    assert ErrorResponse(
        message=error.message,
        error_code=error.error_code,
    ).model_dump() == {
        "success": False,
        "message": "User not found",
        "error_code": "USER_NOT_FOUND",
        "details": {},
    }
