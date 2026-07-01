from typing import Any

from app.repositories.audit_log_repository import AuditLogRepository
from app.utils.datetime import utc_now


SENSITIVE_KEYS = {"password", "password_hash", "new_password", "access_token", "token"}


def _sanitize_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _sanitize_metadata(item)
            for key, item in value.items()
            if key.lower() not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    return value


class AuditLogService:
    def __init__(self, repository: AuditLogRepository | None = None) -> None:
        self.repository = repository or AuditLogRepository()

    async def log_action(
        self,
        user: dict[str, Any] | None,
        action: str,
        entity: str,
        entity_id: Any,
        message: str,
        metadata: dict[str, Any] | None,
        request_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        context = request_context or {}
        data = {
            "user_id": user.get("_id") if user else None,
            "user_role": user.get("role") if user else None,
            "action": action,
            "entity": entity,
            "entity_id": entity_id,
            "message": message,
            "metadata": _sanitize_metadata(metadata or {}),
            "ip_address": context.get("ip_address"),
            "user_agent": context.get("user_agent"),
            "created_at": utc_now(),
        }
        return await self.repository.create_log(data)
