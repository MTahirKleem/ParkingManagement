from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.constants import Currencies, PricingTypes, VehicleTypes


class PricingSnapshotResponse(BaseModel):
    pricing_rule_id: str
    pricing_type: Literal[PricingTypes.FIXED, PricingTypes.HOURLY]
    fixed_rate: float | int | None = None
    base_hours: int | None = None
    base_fee: float | int | None = None
    extra_hour_fee: float | int | None = None
    grace_minutes: int = Field(default=0, ge=0)


class PricingRuleResponse(BaseModel):
    id: str
    vehicle_type: Literal[VehicleTypes.BIKE, VehicleTypes.CAR]
    pricing_type: Literal[PricingTypes.FIXED, PricingTypes.HOURLY]
    fixed_rate: float | int | None = None
    base_hours: int | None = None
    base_fee: float | int | None = None
    extra_hour_fee: float | int | None = None
    grace_minutes: int = Field(default=0, ge=0)
    currency: Literal[Currencies.PKR]
    is_active: bool
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime
