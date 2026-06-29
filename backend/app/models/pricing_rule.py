from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class PricingRule(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId | None = Field(default=None, alias="_id")
    vehicle_type: str
    pricing_type: str
    fixed_rate: float | int | None = None
    base_hours: int | None = None
    base_fee: float | int | None = None
    extra_hour_fee: float | int | None = None
    grace_minutes: int = 0
    currency: str
    is_active: bool
    created_by: ObjectId | None = None
    updated_by: ObjectId | None = None
    created_at: datetime
    updated_at: datetime

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude={"id"})
