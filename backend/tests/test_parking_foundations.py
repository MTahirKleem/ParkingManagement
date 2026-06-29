from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from app.core.constants import (
    AuditActions,
    ErrorCodes,
    ParkingStatus,
    PaymentMethods,
    PricingTypes,
    VehicleTypes,
)
from app.schemas.parking import (
    ParkingActiveQuery,
    ParkingEntryRequest,
    ParkingExitRequest,
    ParkingHistoryQuery,
    ParkingSearchQuery,
    ParkingUpdateRequest,
)
from app.schemas.pricing import PricingSnapshotResponse
from app.utils.plate import normalize_plate_number


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("LEA-1234", "LEA1234"),
        ("LEA 1234", "LEA1234"),
        ("lea1234", "LEA1234"),
        ("LEA@1234", "LEA1234"),
        ("  l-e_a. 12/34 ", "LEA1234"),
    ],
)
def test_plate_normalization_keeps_only_uppercase_letters_and_numbers(
    value: str, expected: str
) -> None:
    assert normalize_plate_number(value) == expected


def test_parking_constants_cover_prompt_values_and_actions() -> None:
    assert VehicleTypes.ALL == ("bike", "car")
    assert ParkingStatus.ALL == ("active", "completed", "cancelled", "deleted")
    assert PaymentMethods.CASH == "cash"
    assert PricingTypes.ALL == ("fixed", "hourly")
    assert AuditActions.VEHICLE_ENTRY_CREATED == "VEHICLE_ENTRY_CREATED"
    assert AuditActions.PARKING_RECORD_DELETED == "PARKING_RECORD_DELETED"
    assert ErrorCodes.DUPLICATE_ACTIVE_VEHICLE == "DUPLICATE_ACTIVE_VEHICLE"
    assert ErrorCodes.PRICING_RULE_NOT_FOUND == "PRICING_RULE_NOT_FOUND"


def test_entry_requires_nonempty_plate_and_valid_vehicle_type() -> None:
    request = ParkingEntryRequest(
        plate_number="  LEA-1234  ",
        vehicle_type="bike",
        slot=" A-12 ",
    )

    assert request.plate_number == "LEA-1234"
    assert request.slot == "A-12"

    with pytest.raises(ValidationError):
        ParkingEntryRequest(plate_number="  ", vehicle_type="bike")
    with pytest.raises(ValidationError):
        ParkingEntryRequest(plate_number="LEA-1234", vehicle_type="truck")


def test_exit_requires_confirmed_cash_receipt() -> None:
    assert ParkingExitRequest(payment_received=True).payment_received is True

    with pytest.raises(ValidationError):
        ParkingExitRequest(payment_received=False)


def test_update_allows_only_prompt_fields_and_requires_one() -> None:
    request = ParkingUpdateRequest(slot=None, notes="Corrected")

    assert request.model_dump(exclude_unset=True) == {
        "slot": None,
        "notes": "Corrected",
    }

    with pytest.raises(ValidationError):
        ParkingUpdateRequest()
    with pytest.raises(ValidationError):
        ParkingUpdateRequest(fee=100)


def test_query_schemas_validate_pagination_enums_and_date_order() -> None:
    active = ParkingActiveQuery(page=1, limit=100, vehicle_type="car", search="lea")
    history = ParkingHistoryQuery(
        page=2,
        limit=20,
        status="completed",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 29),
    )
    search = ParkingSearchQuery(plate_number="LEA-1234", status="active")

    assert active.limit == 100
    assert history.status == "completed"
    assert search.plate_number == "LEA-1234"

    with pytest.raises(ValidationError):
        ParkingActiveQuery(page=0)
    with pytest.raises(ValidationError):
        ParkingActiveQuery(limit=101)
    with pytest.raises(ValidationError):
        ParkingHistoryQuery(status="deleted")
    with pytest.raises(ValidationError):
        ParkingHistoryQuery(
            start_date=date(2026, 6, 30),
            end_date=date(2026, 6, 1),
        )


def test_pricing_snapshot_response_accepts_serialized_object_id() -> None:
    snapshot = PricingSnapshotResponse(
        pricing_rule_id="507f1f77bcf86cd799439011",
        pricing_type="fixed",
        fixed_rate=50,
        base_hours=None,
        base_fee=None,
        extra_hour_fee=None,
        grace_minutes=0,
    )

    assert snapshot.fixed_rate == 50
    assert snapshot.pricing_type == "fixed"
