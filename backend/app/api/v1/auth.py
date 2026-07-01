from typing import Any

from fastapi import APIRouter, Depends, Request

from app.core.permissions import get_current_user
from app.schemas.auth import LoginData, LoginRequest, RefreshTokenData
from app.schemas.common import SuccessResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service() -> AuthService:
    return AuthService()


def _request_context(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


@router.post("/login", response_model=SuccessResponse[LoginData])
async def login(
    payload: LoginRequest,
    request: Request,
    service: AuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    data = await service.login(
        str(payload.email),
        payload.password,
        _request_context(request),
    )
    return {"success": True, "message": "Login successful", "data": data}


@router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    return {
        "success": True,
        "message": "Current user fetched successfully",
        "data": service.get_current_user_profile(current_user),
    }


@router.post("/refresh", response_model=SuccessResponse[RefreshTokenData])
async def refresh_token(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, Any]:
    return {
        "success": True,
        "message": "Token refreshed successfully",
        "data": service.refresh_access_token(current_user),
    }
