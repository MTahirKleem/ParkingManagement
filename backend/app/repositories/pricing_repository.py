from typing import Any

from app.core.constants import Collections
from app.database.mongodb import get_collection
from app.utils.object_id import to_object_id


class PricingRepository:
    def __init__(self, collection: Any = None) -> None:
        self.collection = (
            collection
            if collection is not None
            else get_collection(Collections.PRICING_RULES)
        )

    async def find_active_by_vehicle_type(
        self, vehicle_type: str
    ) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"vehicle_type": vehicle_type, "is_active": True}
        )

    async def create_pricing_rule(
        self, data: dict[str, Any]
    ) -> dict[str, Any]:
        result = await self.collection.insert_one(data)
        return await self.collection.find_one({"_id": result.inserted_id})

    async def find_by_id(self, pricing_id: str) -> dict[str, Any] | None:
        return await self.collection.find_one(
            {"_id": to_object_id(pricing_id)}
        )
