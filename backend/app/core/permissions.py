from typing import Any, Callable, Coroutine

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError

from app.core.constants import ErrorCodes, UserRoles, UserStatus
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.common import AppException
from app.utils.object_id import is_valid_object_id


bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repository_factory() -> Callable[[], UserRepository]:
    return UserRepository


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repository_factory: Callable[[], UserRepository] = Depends(
        get_user_repository_factory
    ),
) -> dict[str, Any]:
    if credentials is None:
        raise AppException(
            status_code=401,
            message="Authentication credentials were not provided",
            error_code=ErrorCodes.UNAUTHORIZED,
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except ExpiredSignatureError as exc:
        raise AppException(
            status_code=401,
            message="Access token has expired",
            error_code=ErrorCodes.TOKEN_EXPIRED,
        ) from exc
    except JWTError as exc:
        raise AppException(
            status_code=401,
            message="Access token is invalid",
            error_code=ErrorCodes.TOKEN_INVALID,
        ) from exc

    user_id = payload.get("sub")
    token_role = payload.get("role")
    if (
        not isinstance(user_id, str)
        or not is_valid_object_id(user_id)
        or token_role not in UserRoles.ALL
    ):
        raise AppException(
            status_code=401,
            message="Access token is invalid",
            error_code=ErrorCodes.TOKEN_INVALID,
        )

    user = await repository_factory().find_by_id(user_id)
    if not user:
        raise AppException(
            status_code=401,
            message="Authenticated user no longer exists",
            error_code=ErrorCodes.UNAUTHORIZED,
        )
    if user.get("status") != UserStatus.ACTIVE:
        raise AppException(
            status_code=403,
            message="User account is inactive",
            error_code=ErrorCodes.USER_INACTIVE,
        )
    if user.get("role") != token_role:
        raise AppException(
            status_code=401,
            message="Access token is invalid",
            error_code=ErrorCodes.TOKEN_INVALID,
        )
    return user


def require_roles(
    *allowed_roles: str,
) -> Callable[..., Coroutine[Any, Any, dict[str, Any]]]:
    async def role_dependency(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        if current_user.get("role") not in allowed_roles:
            raise AppException(
                status_code=403,
                message="You do not have permission to perform this action",
                error_code=ErrorCodes.FORBIDDEN,
            )
        return current_user

    return role_dependency


async def require_admin(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    if current_user.get("role") != UserRoles.ADMIN:
        raise AppException(
            status_code=403,
            message="Administrator access is required",
            error_code=ErrorCodes.FORBIDDEN,
        )
    return current_user
