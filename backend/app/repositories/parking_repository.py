import re
from typing import Any

from pymongo import ReturnDocument

from app.core.constants import Collections, ParkingStatus
from app.database.mongodb import get_collection
from app.utils.datetime import utc_now
from app.utils.object_id import to_object_id


class ParkingRepository:
    def __init__(self, collection: Any = None) -> None:
        self.collection = (
            collection
            if collection is not None
            else get_collection(Collections.PARKING_RECORDS)
        )

    async def create_record(
        self, data: dict[str, Any]
    ) -> dict[str, Any]:
        result = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def find_by_id(self, record_id: str) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"_id": to_object_id(record_id)}
        )

    async def find_active_by_id(
        self, record_id: str
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {
                "_id": to_object_id(record_id),
                "status": ParkingStatus.ACTIVE,
            }
        )

    async def find_active_by_normalized_plate(
        self, normalized_plate_number: str
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {
                "normalized_plate_number": normalized_plate_number,
                "status": ParkingStatus.ACTIVE,
            }
        )

    async def find_duplicate_active_plate(
        self,
        normalized_plate_number: str,
        exclude_id: str | None = None,
    ) -> dict[str, Any] | None:
        query: dict[str, Any] = {
            "normalized_plate_number": normalized_plate_number,
            "status": ParkingStatus.ACTIVE,
        }
        if exclude_id is not None:
            query["_id"] = {"$ne": to_object_id(exclude_id)}
        return await self.collection.find_one(query)

    @staticmethod
    def _active_query(filters: dict[str, Any]) -> dict[str, Any]:
        query: dict[str, Any] = {"status": ParkingStatus.ACTIVE}
        if filters.get("vehicle_type"):
            query["vehicle_type"] = filters["vehicle_type"]
        if filters.get("search"):
            query["normalized_plate_number"] = {
                "$regex": re.escape(filters["search"]),
                "$options": "i",
            }
        return query

    async def list_active(
        self,
        filters: dict[str, Any],
        page: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        cursor = (
            self.collection.find(self._active_query(filters))
            .sort("entry_time", -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_active(self, filters: dict[str, Any]) -> int:
        return await self.collection.count_documents(
            self._active_query(filters)
        )

    @staticmethod
    def _date_bounds(filters: dict[str, Any]) -> dict[str, Any]:
        bounds: dict[str, Any] = {}
        if filters.get("start_at") is not None:
            bounds["$gte"] = filters["start_at"]
        if filters.get("end_before") is not None:
            bounds["$lt"] = filters["end_before"]
        return bounds

    @classmethod
    def _history_query(cls, filters: dict[str, Any]) -> dict[str, Any]:
        status = filters.get("status")
        query: dict[str, Any] = {
            "status": status if status else {"$ne": ParkingStatus.DELETED}
        }
        if filters.get("vehicle_type"):
            query["vehicle_type"] = filters["vehicle_type"]
        if filters.get("search"):
            query["normalized_plate_number"] = {
                "$regex": re.escape(filters["search"]),
                "$options": "i",
            }

        bounds = cls._date_bounds(filters)
        if bounds:
            if status == ParkingStatus.COMPLETED:
                query["exit_time"] = bounds
            elif status in {
                ParkingStatus.ACTIVE,
                ParkingStatus.CANCELLED,
            }:
                query["entry_time"] = bounds
            else:
                query["$or"] = [
                    {
                        "status": ParkingStatus.COMPLETED,
                        "exit_time": bounds,
                    },
                    {
                        "status": {
                            "$in": [
                                ParkingStatus.ACTIVE,
                                ParkingStatus.CANCELLED,
                            ]
                        },
                        "entry_time": bounds,
                    },
                ]
        return query

    async def list_history(
        self,
        filters: dict[str, Any],
        page: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        sort_field = (
            "exit_time"
            if filters.get("status") == ParkingStatus.COMPLETED
            else "created_at"
        )
        cursor = (
            self.collection.find(self._history_query(filters))
            .sort(sort_field, -1)
            .skip((page - 1) * limit)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def count_history(self, filters: dict[str, Any]) -> int:
        return await self.collection.count_documents(
            self._history_query(filters)
        )

    async def search_by_plate(
        self,
        normalized_plate_number: str,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {
            "normalized_plate_number": normalized_plate_number,
            "status": status if status else {"$ne": ParkingStatus.DELETED},
        }
        cursor = self.collection.find(query).sort("created_at", -1)
        return await cursor.to_list(length=None)

    async def update_record(
        self,
        record_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        return await self.collection.find_one_and_update(
            {
                "_id": to_object_id(record_id),
                "status": {"$ne": ParkingStatus.DELETED},
            },
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )

    async def complete_exit(
        self,
        record_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any] | None:
        return await self.collection.find_one_and_update(
            {
                "_id": to_object_id(record_id),
                "status": ParkingStatus.ACTIVE,
            },
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )

    async def soft_delete_record(
        self,
        record_id: str,
        updated_by: str,
    ) -> dict[str, Any] | None:
        return await self.collection.find_one_and_update(
            {
                "_id": to_object_id(record_id),
                "status": {"$ne": ParkingStatus.DELETED},
            },
            {
                "$set": {
                    "status": ParkingStatus.DELETED,
                    "updated_by": to_object_id(updated_by),
                    "updated_at": utc_now(),
                }
            },
            return_document=ReturnDocument.AFTER,
        )
