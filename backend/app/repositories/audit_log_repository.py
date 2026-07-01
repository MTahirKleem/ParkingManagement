from typing import Any

from app.core.constants import Collections
from app.database.mongodb import get_collection
from app.utils.object_id import to_object_id


class AuditLogRepository:
    def __init__(self, collection: Any = None) -> None:
        self.collection = (
            collection
            if collection is not None
            else get_collection(Collections.AUDIT_LOGS)
        )

    async def create_log(self, data: dict[str, Any]) -> dict[str, Any]:
        result = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": result.inserted_id})

    @staticmethod
    def build_filters(filters: dict[str, Any]) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if filters.get("action"):
            query["action"] = filters["action"]
        if filters.get("user_id"):
            query["user_id"] = to_object_id(filters["user_id"])
        if filters.get("entity"):
            query["entity"] = filters["entity"]
        if filters.get("start_date") or filters.get("end_date"):
            created_at: dict[str, Any] = {}
            if filters.get("start_date"):
                created_at["$gte"] = filters["start_date"]
            if filters.get("end_date"):
                created_at["$lte"] = filters["end_date"]
            query["created_at"] = created_at
        return query

    async def list_logs(
        self,
        filters: dict[str, Any],
        page: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find(self.build_filters(filters))
            .sort("created_at", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_logs(self, filters: dict[str, Any]) -> int:
        return await self.collection.count_documents(self.build_filters(filters))
