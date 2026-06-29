from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class Payment(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    method: str
    received: bool
    received_by: ObjectId
    received_at: datetime


class PricingSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    pricing_rule_id: ObjectId
    pricing_type: str
    fixed_rate: float | int | None = None
    base_hours: int | None = None
    base_fee: float | int | None = None
    extra_hour_fee: float | int | None = None
    grace_minutes: int = 0


class ParkingRecord(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId | None = Field(default=None, alias="_id")
    plate_number: str
    normalized_plate_number: str
    vehicle_type: str
    slot: str | None = None
    entry_time: datetime
    exit_time: datetime | None = None
    status: str
    duration_minutes: int | None = None
    fee: float | int | None = None
    currency: str
    payment: Payment | None = None
    pricing_snapshot: PricingSnapshot | None = None
    ocr: dict[str, Any] | None = None
    notes: str | None = None
    created_by: ObjectId
    completed_by: ObjectId | None = None
    updated_by: ObjectId | None = None
    created_at: datetime
    updated_at: datetime

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude={"id"})
