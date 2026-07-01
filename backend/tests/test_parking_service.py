from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.constants import (
    AuditActions,
    ErrorCodes,
    ParkingStatus,
    UserRoles,
)
from app.schemas.common import AppException
from app.schemas.parking import (
    ParkingEntryRequest,
    ParkingExitRequest,
    ParkingUpdateRequest,
)
from app.services.parking_service import ParkingService


def make_user(role=UserRoles.ADMIN):
    return {
        "_id": ObjectId(),
        "name": "Actor",
        "email": "actor@example.com",
        "role": role,
        "status": "active",
    }


def make_record(**overrides):
    now = datetime(2026, 6, 29, 10, 0, tzinfo=timezone.utc)
    record = {
        "_id": ObjectId(),
        "plate_number": "LEA-1234",
        "normalized_plate_number": "LEA1234",
        "vehicle_type": "bike",
        "slot": "A-12",
        "entry_time": now,
        "exit_time": None,
        "status": ParkingStatus.ACTIVE,
        "duration_minutes": None,
        "fee": None,
        "currency": "PKR",
        "payment": None,
        "pricing_snapshot": None,
        "ocr": None,
        "notes": None,
        "created_by": ObjectId(),
        "completed_by": None,
        "updated_by": None,
        "created_at": now,
        "updated_at": now,
    }
    record.update(overrides)
    return record


def make_service(repository=None, pricing=None, audit=None, users=None):
    user_repository = users or AsyncMock()
    if users is None:
        user_repository.find_names_by_ids.return_value = {}
    return ParkingService(
        repository or AsyncMock(),
        pricing or AsyncMock(),
        audit or AsyncMock(),
        user_repository=user_repository,
    )


@pytest.mark.asyncio
async def test_create_entry_builds_active_shape_and_audits() -> None:
    actor = make_user(role=UserRoles.GUARD)
    repository = AsyncMock()
    repository.find_duplicate_active_plate.return_value = None
    repository.create_record.side_effect = lambda data: {
        "_id": ObjectId(),
        **data,
    }
    audit = AsyncMock()
    service = make_service(repository=repository, audit=audit)

    result = await service.create_entry(
        ParkingEntryRequest(
            plate_number="lea-1234",
            vehicle_type="bike",
            slot="A-12",
        ),
        actor,
        {"ip_address": "127.0.0.1"},
    )

    inserted = repository.create_record.await_args.args[0]
    assert inserted["plate_number"] == "LEA-1234"
    assert inserted["normalized_plate_number"] == "LEA1234"
    assert inserted["status"] == ParkingStatus.ACTIVE
    assert inserted["created_by"] == actor["_id"]
    assert inserted["exit_time"] is None
    assert inserted["fee"] is None
    assert inserted["payment"] is None
    assert inserted["pricing_snapshot"] is None
    assert result["id"]
    assert audit.log_action.await_args.kwargs["action"] == AuditActions.VEHICLE_ENTRY_CREATED


@pytest.mark.asyncio
async def test_create_entry_rejects_checked_and_racing_duplicates() -> None:
    repository = AsyncMock()
    repository.find_duplicate_active_plate.return_value = make_record()
    service = make_service(repository=repository)
    request = ParkingEntryRequest(
        plate_number="LEA-1234", vehicle_type="bike"
    )

    with pytest.raises(AppException) as checked:
        await service.create_entry(request, make_user(), {})

    repository.find_duplicate_active_plate.return_value = None
    repository.create_record.side_effect = DuplicateKeyError("duplicate")
    with pytest.raises(AppException) as racing:
        await service.create_entry(request, make_user(), {})

    assert checked.value.status_code == 409
    assert racing.value.error_code == ErrorCodes.DUPLICATE_ACTIVE_VEHICLE


@pytest.mark.asyncio
async def test_complete_exit_embeds_payment_pricing_and_audits(monkeypatch) -> None:
    actor = make_user(role=UserRoles.GUARD)
    record = make_record()
    repository = AsyncMock()
    repository.find_by_id.return_value = record
    pricing = AsyncMock()
    pricing.calculate_fee.return_value = {
        "duration_minutes": 135,
        "fee": 50,
        "currency": "PKR",
        "pricing_snapshot": {
            "pricing_rule_id": ObjectId(),
            "pricing_type": "fixed",
            "fixed_rate": 50,
            "base_hours": None,
            "base_fee": None,
            "extra_hour_fee": None,
            "grace_minutes": 0,
        },
    }
    repository.complete_exit.side_effect = lambda _id, data: {
        **record,
        **data,
    }
    audit = AsyncMock()
    service = make_service(repository, pricing, audit)

    result = await service.complete_exit(
        str(record["_id"]),
        ParkingExitRequest(payment_received=True),
        actor,
        {},
    )

    update = repository.complete_exit.await_args.args[1]
    assert update["status"] == ParkingStatus.COMPLETED
    assert update["duration_minutes"] == 135
    assert update["payment"]["method"] == "cash"
    assert update["payment"]["received_by"] == actor["_id"]
    assert update["completed_by"] == actor["_id"]
    assert update["pricing_snapshot"]["fixed_rate"] == 50
    assert result["payment"]["received_by"] == str(actor["_id"])
    assert audit.log_action.await_args.kwargs["action"] == AuditActions.VEHICLE_EXIT_COMPLETED


@pytest.mark.asyncio
async def test_complete_exit_rejects_invalid_missing_deleted_and_completed() -> None:
    repository = AsyncMock()
    service = make_service(repository=repository)
    request = ParkingExitRequest(payment_received=True)

    with pytest.raises(AppException) as invalid:
        await service.complete_exit("invalid", request, make_user(), {})

    repository.find_by_id.return_value = None
    with pytest.raises(AppException) as missing:
        await service.complete_exit(str(ObjectId()), request, make_user(), {})

    repository.find_by_id.return_value = make_record(status="deleted")
    with pytest.raises(AppException) as deleted:
        await service.complete_exit(str(ObjectId()), request, make_user(), {})

    repository.find_by_id.return_value = make_record(status="completed")
    with pytest.raises(AppException) as completed:
        await service.complete_exit(str(ObjectId()), request, make_user(), {})

    assert invalid.value.status_code == 400
    assert missing.value.error_code == ErrorCodes.PARKING_RECORD_NOT_FOUND
    assert deleted.value.status_code == 404
    assert completed.value.error_code == ErrorCodes.VEHICLE_ALREADY_COMPLETED


@pytest.mark.asyncio
async def test_active_and_history_lists_normalize_filters_and_paginate() -> None:
    repository = AsyncMock()
    record = make_record()
    repository.list_active.return_value = [record]
    repository.count_active.return_value = 1
    repository.list_history.return_value = [record]
    repository.count_history.return_value = 1
    service = make_service(repository=repository)

    active = await service.get_active_vehicles(
        {"page": 1, "limit": 20, "search": "lea-12", "vehicle_type": "bike"}
    )
    history = await service.get_history(
        {
            "page": 1,
            "limit": 20,
            "status": "completed",
            "start_date": date(2026, 6, 1),
            "end_date": date(2026, 6, 29),
            "search": "lea 12",
        }
    )

    assert active["pagination"]["pages"] == 1
    assert active["data"][0]["id"] == str(record["_id"])
    active_filters = repository.list_active.await_args.args[0]
    assert active_filters["search"] == "LEA12"
    history_filters = repository.list_history.await_args.args[0]
    assert history_filters["search"] == "LEA12"
    assert history_filters["start_at"] == datetime(
        2026, 6, 1, tzinfo=timezone.utc
    )
    assert history_filters["end_before"] == datetime(
        2026, 6, 30, tzinfo=timezone.utc
    )
    assert history["pagination"]["total"] == 1


@pytest.mark.asyncio
async def test_search_and_detail_hide_deleted_records() -> None:
    active = make_record()
    repository = AsyncMock()
    repository.search_by_plate.return_value = [active]
    repository.find_by_id.side_effect = [active, make_record(status="deleted")]
    service = make_service(repository=repository)

    results = await service.search_records("lea-1234", "active")
    detail = await service.get_record_by_id(str(active["_id"]))

    assert results[0]["normalized_plate_number"] == "LEA1234"
    assert detail["id"] == str(active["_id"])
    repository.search_by_plate.assert_awaited_once_with("LEA1234", "active")

    with pytest.raises(AppException) as deleted:
        await service.get_record_by_id(str(ObjectId()))
    assert deleted.value.status_code == 404


@pytest.mark.asyncio
async def test_parking_detail_resolves_user_names_with_missing_user_fallback() -> None:
    creator_id = ObjectId()
    receiver_id = ObjectId()
    record = make_record(
        status=ParkingStatus.COMPLETED,
        created_by=creator_id,
        completed_by=receiver_id,
        payment={
            "method": "cash",
            "received": True,
            "received_by": receiver_id,
            "received_at": datetime(2026, 6, 29, 12, 0, tzinfo=timezone.utc),
        },
    )
    repository = AsyncMock()
    repository.find_by_id.return_value = record
    users = AsyncMock()
    users.find_names_by_ids.return_value = {
        str(creator_id): "Entry Guard",
    }
    service = make_service(repository=repository, users=users)

    result = await service.get_record_by_id(str(record["_id"]))

    users.find_names_by_ids.assert_awaited_once_with(
        {str(creator_id), str(receiver_id)}
    )
    assert result["created_by_name"] == "Entry Guard"
    assert result["completed_by_name"] is None
    assert result["payment"]["received_by_name"] is None


@pytest.mark.asyncio
async def test_admin_update_renormalizes_plate_checks_duplicate_and_audits() -> None:
    actor = make_user()
    record = make_record()
    repository = AsyncMock()
    repository.find_by_id.return_value = record
    repository.find_duplicate_active_plate.return_value = None
    repository.update_record.side_effect = lambda _id, data: {
        **record,
        **data,
    }
    audit = AsyncMock()
    service = make_service(repository=repository, audit=audit)

    result = await service.update_record(
        str(record["_id"]),
        ParkingUpdateRequest(
            plate_number="lea 9999",
            vehicle_type="car",
            slot="B-05",
            notes="Corrected",
        ),
        actor,
        {},
    )

    update = repository.update_record.await_args.args[1]
    assert update["plate_number"] == "LEA 9999"
    assert update["normalized_plate_number"] == "LEA9999"
    assert update["updated_by"] == actor["_id"]
    assert result["vehicle_type"] == "car"
    assert audit.log_action.await_args.kwargs["action"] == AuditActions.PARKING_RECORD_UPDATED


@pytest.mark.asyncio
async def test_active_update_rejects_duplicate_plate() -> None:
    record = make_record()
    repository = AsyncMock()
    repository.find_by_id.return_value = record
    repository.find_duplicate_active_plate.return_value = make_record()
    service = make_service(repository=repository)

    with pytest.raises(AppException) as caught:
        await service.update_record(
            str(record["_id"]),
            ParkingUpdateRequest(plate_number="LEA-2222"),
            make_user(),
            {},
        )

    assert caught.value.error_code == ErrorCodes.DUPLICATE_ACTIVE_VEHICLE
    repository.update_record.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_soft_deletes_and_audits() -> None:
    actor = make_user()
    record = make_record()
    repository = AsyncMock()
    repository.find_by_id.return_value = record
    repository.soft_delete_record.return_value = {
        **record,
        "status": "deleted",
    }
    audit = AsyncMock()
    service = make_service(repository=repository, audit=audit)

    result = await service.delete_record(
        str(record["_id"]), actor, {"user_agent": "pytest"}
    )

    repository.soft_delete_record.assert_awaited_once_with(
        str(record["_id"]), str(actor["_id"])
    )
    assert result == {"id": str(record["_id"]), "status": "deleted"}
    assert audit.log_action.await_args.kwargs["action"] == AuditActions.PARKING_RECORD_DELETED
