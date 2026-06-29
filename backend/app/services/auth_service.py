from typing import Any

from app.core.constants import AuditActions, ErrorCodes, UserStatus
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.common import AppException
from app.services.audit_log_service import AuditLogService
from app.utils.object_id import serialize_document


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        audit_log_service: AuditLogService | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.audit_log_service = audit_log_service or AuditLogService()

    async def _log_failed_login(
        self,
        user: dict[str, Any] | None,
        email: str,
        request_context: dict[str, Any] | None,
    ) -> None:
        await self.audit_log_service.log_action(
            user=user,
            action=AuditActions.USER_LOGIN_FAILED,
            entity="user",
            entity_id=user.get("_id") if user else None,
            message="User login failed",
            metadata={"email": email},
            request_context=request_context,
        )

    async def login(
        self,
        email: str,
        password: str,
        request_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        normalized_email = email.strip().lower()
        user = await self.user_repository.find_by_email(normalized_email)
        password_valid = False
        if user:
            try:
                password_valid = verify_password(password, user["password_hash"])
            except (TypeError, ValueError):
                password_valid = False

        if not user or not password_valid:
            await self._log_failed_login(user, normalized_email, request_context)
            raise AppException(
                status_code=401,
                message="Invalid email or password",
                error_code=ErrorCodes.INVALID_CREDENTIALS,
            )

        if user.get("status") != UserStatus.ACTIVE:
            await self._log_failed_login(user, normalized_email, request_context)
            raise AppException(
                status_code=403,
                message="User account is inactive",
                error_code=ErrorCodes.USER_INACTIVE,
            )

        updated_user = await self.user_repository.update_last_login(str(user["_id"]))
        user = updated_user or user
        await self.audit_log_service.log_action(
            user=user,
            action=AuditActions.USER_LOGIN,
            entity="user",
            entity_id=user["_id"],
            message="User logged in successfully",
            metadata={"email": user["email"]},
            request_context=request_context,
        )
        return {
            "access_token": create_access_token(
                {"sub": str(user["_id"]), "role": user["role"]}
            ),
            "token_type": "bearer",
            "user": self._auth_user(user),
        }

    @staticmethod
    def _auth_user(user: dict[str, Any]) -> dict[str, Any]:
        serialized = serialize_document(user)
        return {
            key: serialized[key]
            for key in ("id", "name", "email", "role", "status")
        }

    @staticmethod
    def get_current_user_profile(user: dict[str, Any]) -> dict[str, Any]:
        serialized = serialize_document(user)
        serialized.pop("password_hash", None)
        return serialized

    @staticmethod
    def refresh_access_token(user: dict[str, Any]) -> dict[str, str]:
        return {
            "access_token": create_access_token(
                {"sub": str(user["_id"]), "role": user["role"]}
            ),
            "token_type": "bearer",
        }
