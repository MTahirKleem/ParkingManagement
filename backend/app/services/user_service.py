from math import ceil
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.core.constants import AuditActions, ErrorCodes, UserRoles, UserStatus
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.common import AppException
from app.schemas.user import UserCreateRequest, UserUpdateRequest
from app.services.audit_log_service import AuditLogService
from app.utils.datetime import utc_now
from app.utils.object_id import is_valid_object_id, serialize_document


class UserService:
    def __init__(
        self,
        user_repository: UserRepository | None = None,
        audit_log_service: AuditLogService | None = None,
    ) -> None:
        self.user_repository = user_repository or UserRepository()
        self.audit_log_service = audit_log_service or AuditLogService()

    @staticmethod
    def _safe_user(user: dict[str, Any]) -> dict[str, Any]:
        result = serialize_document(user)
        result.pop("password_hash", None)
        return result

    @staticmethod
    def _validate_id(user_id: str) -> None:
        if not is_valid_object_id(user_id):
            raise AppException(
                status_code=400,
                message="Invalid user ID",
                error_code=ErrorCodes.VALIDATION_ERROR,
                details={"user_id": "Must be a valid ObjectId"},
            )

    async def _get_required_user(self, user_id: str) -> dict[str, Any]:
        self._validate_id(user_id)
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise AppException(
                status_code=404,
                message="User not found",
                error_code=ErrorCodes.USER_NOT_FOUND,
            )
        return user

    async def create_guard(
        self,
        request_data: UserCreateRequest,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        email = str(request_data.email).lower()
        if await self.user_repository.find_by_email(email):
            raise AppException(
                status_code=409,
                message="A user with this email already exists",
                error_code=ErrorCodes.USER_ALREADY_EXISTS,
            )

        now = utc_now()
        document = {
            "name": request_data.name,
            "email": email,
            "phone": request_data.phone,
            "password_hash": hash_password(request_data.password),
            "role": UserRoles.GUARD,
            "status": UserStatus.ACTIVE,
            "last_login_at": None,
            "created_by": current_user["_id"],
            "updated_by": current_user["_id"],
            "created_at": now,
            "updated_at": now,
        }
        try:
            user = await self.user_repository.create_user(document)
        except DuplicateKeyError as exc:
            raise AppException(
                status_code=409,
                message="A user with this email already exists",
                error_code=ErrorCodes.USER_ALREADY_EXISTS,
            ) from exc

        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.USER_CREATED,
            entity="user",
            entity_id=user["_id"],
            message="Guard user created",
            metadata={"email": user["email"]},
            request_context=request_context,
        )
        return self._safe_user(user)

    async def list_users(self, filters: dict[str, Any]) -> dict[str, Any]:
        page = filters.get("page", 1)
        limit = filters.get("limit", 20)
        repository_filters = {
            key: value
            for key, value in filters.items()
            if key in {"role", "status", "search"} and value is not None
        }
        users = await self.user_repository.list_users(
            repository_filters, page, limit
        )
        total = await self.user_repository.count_users(repository_filters)
        return {
            "data": [self._safe_user(user) for user in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": ceil(total / limit) if total else 0,
            },
        }

    async def get_user_by_id(self, user_id: str) -> dict[str, Any]:
        return self._safe_user(await self._get_required_user(user_id))

    async def update_user(
        self,
        user_id: str,
        request_data: UserUpdateRequest,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await self._get_required_user(user_id)
        updates = request_data.model_dump(exclude_unset=True)
        updates.update(
            {
                "updated_by": current_user["_id"],
                "updated_at": utc_now(),
            }
        )
        user = await self.user_repository.update_user(user_id, updates)
        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.USER_UPDATED,
            entity="user",
            entity_id=user["_id"],
            message="User updated",
            metadata={"updated_fields": sorted(request_data.model_fields_set)},
            request_context=request_context,
        )
        return self._safe_user(user)

    async def delete_user(
        self,
        user_id: str,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        target = await self._get_required_user(user_id)
        if target["_id"] == current_user["_id"]:
            raise AppException(
                status_code=403,
                message="You cannot delete your own account",
                error_code=ErrorCodes.FORBIDDEN,
            )
        user = await self.user_repository.soft_delete_user(
            user_id, str(current_user["_id"])
        )
        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.USER_DELETED,
            entity="user",
            entity_id=target["_id"],
            message="User soft deleted",
            metadata={"email": target["email"]},
            request_context=request_context,
        )
        return {"id": str(user["_id"]), "status": user["status"]}

    async def reset_password(
        self,
        user_id: str,
        new_password: str,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        target = await self._get_required_user(user_id)
        await self.user_repository.update_password(
            user_id,
            hash_password(new_password),
            str(current_user["_id"]),
        )
        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.USER_PASSWORD_RESET,
            entity="user",
            entity_id=target["_id"],
            message="User password reset",
            metadata={"email": target["email"]},
            request_context=request_context,
        )
        return {"id": str(target["_id"])}
