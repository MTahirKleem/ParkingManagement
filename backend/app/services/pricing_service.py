from datetime import datetime, timezone
from math import ceil
from typing import Any

from app.core.constants import ErrorCodes, PricingTypes
from app.repositories.pricing_repository import PricingRepository
from app.schemas.common import AppException


def _utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class PricingService:
    def __init__(
        self, pricing_repository: PricingRepository | None = None
    ) -> None:
        self.pricing_repository = pricing_repository or PricingRepository()

    async def get_active_pricing_rule(
        self, vehicle_type: str
    ) -> dict[str, Any]:
        rule = await self.pricing_repository.find_active_by_vehicle_type(
            vehicle_type
        )
        if not rule:
            raise AppException(
                status_code=404,
                message="Active pricing rule not found",
                error_code=ErrorCodes.PRICING_RULE_NOT_FOUND,
            )
        return rule

    async def calculate_fee(
        self,
        vehicle_type: str,
        entry_time: datetime,
        exit_time: datetime,
    ) -> dict[str, Any]:
        rule = await self.get_active_pricing_rule(vehicle_type)
        duration_seconds = (
            _utc_datetime(exit_time) - _utc_datetime(entry_time)
        ).total_seconds()
        duration_minutes = max(0, ceil(duration_seconds / 60))

        if rule["pricing_type"] == PricingTypes.FIXED:
            fee = rule["fixed_rate"]
        elif rule["pricing_type"] == PricingTypes.HOURLY:
            duration_after_grace = max(
                0, duration_minutes - rule.get("grace_minutes", 0)
            )
            duration_hours = ceil(duration_after_grace / 60)
            if duration_hours <= rule["base_hours"]:
                fee = rule["base_fee"]
            else:
                extra_hours = duration_hours - rule["base_hours"]
                fee = rule["base_fee"] + (
                    extra_hours * rule["extra_hour_fee"]
                )
        else:
            raise ValueError("Unsupported pricing type")

        return {
            "duration_minutes": duration_minutes,
            "fee": fee,
            "currency": rule["currency"],
            "pricing_snapshot": {
                "pricing_rule_id": rule["_id"],
                "pricing_type": rule["pricing_type"],
                "fixed_rate": rule.get("fixed_rate"),
                "base_hours": rule.get("base_hours"),
                "base_fee": rule.get("base_fee"),
                "extra_hour_fee": rule.get("extra_hour_fee"),
                "grace_minutes": rule.get("grace_minutes", 0),
            },
        }
