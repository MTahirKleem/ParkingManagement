import re
from typing import Any

from pymongo import ReturnDocument

from app.core.constants import Collections, UserStatus
from app.database.mongodb import get_collection
from app.utils.datetime import utc_now
from app.utils.object_id import is_valid_object_id, to_object_id


class UserRepository:
    def __init__(self, collection: Any = None) -> None:
        self.collection = (
            collection
            if collection is not None
            else get_collection(Collections.USERS)
        )

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"email": email.strip().lower()})

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"_id": to_object_id(user_id)})

    async def find_names_by_ids(
        self, user_ids: set[str]
    ) -> dict[str, str]:
        object_ids = [
            to_object_id(user_id)
            for user_id in user_ids
            if is_valid_object_id(user_id)
        ]
        if not object_ids:
            return {}
        cursor = self.collection.find(
            {"_id": {"$in": object_ids}},
            {"name": 1},
        )
        users = await cursor.to_list(length=len(object_ids))
        return {
            str(user["_id"]): user["name"]
            for user in users
            if user.get("name")
        }

    async def create_user(self, data: dict[str, Any]) -> dict[str, Any]:
        result = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": result.inserted_id})

    @staticmethod
    def build_filters(filters: dict[str, Any]) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if filters.get("role"):
            query["role"] = filters["role"]
        if filters.get("status"):
            query["status"] = filters["status"]
        if filters.get("search"):
            pattern = re.escape(filters["search"].strip())
            query["$or"] = [
                {"name": {"$regex": pattern, "$options": "i"}},
                {"email": {"$regex": pattern, "$options": "i"}},
            ]
        return query

    async def list_users(
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

    async def count_users(self, filters: dict[str, Any]) -> int:
        return await self.collection.count_documents(self.build_filters(filters))

    async def update_user(
        self,
        user_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        return await self.collection.find_one_and_update(
            {"_id": to_object_id(user_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )

    async def soft_delete_user(
        self,
        user_id: str,
        updated_by: str,
    ) -> dict[str, Any] | None:
        return await self.update_user(
            user_id,
            {
                "status": UserStatus.DELETED,
                "updated_by": to_object_id(updated_by),
                "updated_at": utc_now(),
            },
        )

    async def update_last_login(self, user_id: str) -> dict[str, Any] | None:
        now = utc_now()
        return await self.update_user(
            user_id,
            {"last_login_at": now, "updated_at": now},
        )

    async def update_password(
        self,
        user_id: str,
        password_hash: str,
        updated_by: str,
    ) -> dict[str, Any] | None:
        return await self.update_user(
            user_id,
            {
                "password_hash": password_hash,
                "updated_by": to_object_id(updated_by),
                "updated_at": utc_now(),
            },
        )
