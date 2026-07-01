from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.core.constants import ErrorCodes
from app.repositories.pricing_repository import PricingRepository
from app.schemas.common import AppException
from app.services.pricing_service import PricingService


@pytest.mark.asyncio
async def test_pricing_repository_supports_required_operations() -> None:
    rule_id = ObjectId()
    rule = {"_id": rule_id, "vehicle_type": "bike", "is_active": True}
    collection = MagicMock()
    collection.find_one = AsyncMock(side_effect=[rule, rule, rule])
    collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=rule_id)
    )
    repository = PricingRepository(collection)

    active = await repository.find_active_by_vehicle_type("bike")
    created = await repository.create_pricing_rule(
        {"vehicle_type": "bike", "is_active": True}
    )
    fetched = await repository.find_by_id(str(rule_id))

    assert active == rule
    assert created == rule
    assert fetched == rule
    collection.find_one.assert_any_await(
        {"vehicle_type": "bike", "is_active": True}
    )
    collection.find_one.assert_any_await({"_id": rule_id})


@pytest.mark.asyncio
async def test_pricing_service_rejects_missing_active_rule() -> None:
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.return_value = None
    service = PricingService(repository)

    with pytest.raises(AppException) as caught:
        await service.get_active_pricing_rule("bike")

    assert caught.value.status_code == 404
    assert caught.value.error_code == ErrorCodes.PRICING_RULE_NOT_FOUND


@pytest.mark.asyncio
async def test_fixed_pricing_returns_rate_duration_and_snapshot() -> None:
    rule_id = ObjectId()
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.return_value = {
        "_id": rule_id,
        "vehicle_type": "bike",
        "pricing_type": "fixed",
        "fixed_rate": 50,
        "base_hours": None,
        "base_fee": None,
        "extra_hour_fee": None,
        "grace_minutes": 0,
        "currency": "PKR",
        "is_active": True,
    }
    service = PricingService(repository)
    entry = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)

    result = await service.calculate_fee(
        "bike", entry, entry + timedelta(minutes=135)
    )

    assert result["duration_minutes"] == 135
    assert result["fee"] == 50
    assert result["currency"] == "PKR"
    assert result["pricing_snapshot"] == {
        "pricing_rule_id": rule_id,
        "pricing_type": "fixed",
        "fixed_rate": 50,
        "base_hours": None,
        "base_fee": None,
        "extra_hour_fee": None,
        "grace_minutes": 0,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("minutes", "expected_fee"),
    [
        (5, 100),
        (10, 100),
        (120, 100),
        (130, 100),
        (131, 150),
        (190, 150),
        (191, 200),
    ],
)
async def test_hourly_pricing_applies_grace_base_and_rounded_extra_hours(
    minutes: int, expected_fee: int
) -> None:
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.return_value = {
        "_id": ObjectId(),
        "vehicle_type": "car",
        "pricing_type": "hourly",
        "fixed_rate": None,
        "base_hours": 2,
        "base_fee": 100,
        "extra_hour_fee": 50,
        "grace_minutes": 10,
        "currency": "PKR",
        "is_active": True,
    }
    service = PricingService(repository)
    entry = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)

    result = await service.calculate_fee(
        "car", entry, entry + timedelta(minutes=minutes)
    )

    assert result["duration_minutes"] == minutes
    assert result["fee"] == expected_fee


@pytest.mark.asyncio
async def test_duration_rounds_partial_minutes_up_and_never_negative() -> None:
    repository = AsyncMock()
    repository.find_active_by_vehicle_type.return_value = {
        "_id": ObjectId(),
        "vehicle_type": "bike",
        "pricing_type": "fixed",
        "fixed_rate": 50,
        "base_hours": None,
        "base_fee": None,
        "extra_hour_fee": None,
        "grace_minutes": 0,
        "currency": "PKR",
        "is_active": True,
    }
    service = PricingService(repository)
    entry = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)

    partial = await service.calculate_fee(
        "bike", entry, entry + timedelta(seconds=61)
    )
    negative = await service.calculate_fee(
        "bike", entry, entry - timedelta(minutes=1)
    )

    assert partial["duration_minutes"] == 2
    assert negative["duration_minutes"] == 0
