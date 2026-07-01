from typing import Any, Literal

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.constants import UserRoles, UserStatus
from app.core.permissions import require_admin
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.user import (
    DeletedUserResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service() -> UserService:
    return UserService()


def _request_context(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


@router.post(
    "",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_guard(
    payload: UserCreateRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    data = await service.create_guard(
        payload, current_user, _request_context(request)
    )
    return {"success": True, "message": "Guard created successfully", "data": data}


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    role: Literal[UserRoles.ADMIN, UserRoles.GUARD] | None = None,
    user_status: Literal[
        UserStatus.ACTIVE,
        UserStatus.INACTIVE,
        UserStatus.DELETED,
    ]
    | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, min_length=1),
    _: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    result = await service.list_users(
        {
            "page": page,
            "limit": limit,
            "role": role,
            "status": user_status,
            "search": search,
        }
    )
    return {
        "success": True,
        "message": "Users fetched successfully",
        **result,
    }


@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: str,
    _: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    return {
        "success": True,
        "message": "User fetched successfully",
        "data": await service.get_user_by_id(user_id),
    }


@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
async def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    data = await service.update_user(
        user_id, payload, current_user, _request_context(request)
    )
    return {"success": True, "message": "User updated successfully", "data": data}


@router.delete("/{user_id}", response_model=SuccessResponse[DeletedUserResponse])
async def delete_user(
    user_id: str,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    data = await service.delete_user(
        user_id, current_user, _request_context(request)
    )
    return {"success": True, "message": "User deleted successfully", "data": data}


@router.post(
    "/{user_id}/reset-password",
    response_model=SuccessResponse[PasswordResetResponse],
)
async def reset_password(
    user_id: str,
    payload: PasswordResetRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: UserService = Depends(get_user_service),
) -> dict[str, Any]:
    data = await service.reset_password(
        user_id,
        payload.new_password,
        current_user,
        _request_context(request),
    )
    return {"success": True, "message": "Password reset successfully", "data": data}
