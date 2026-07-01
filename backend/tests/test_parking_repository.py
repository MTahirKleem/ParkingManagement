from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from pymongo import ReturnDocument

from app.repositories.parking_repository import ParkingRepository


def make_collection():
    collection = MagicMock()
    collection.find_one = AsyncMock()
    collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=ObjectId())
    )
    collection.find_one_and_update = AsyncMock()
    collection.count_documents = AsyncMock(return_value=0)
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])
    collection.find.return_value = cursor
    return collection, cursor


@pytest.mark.asyncio
async def test_create_and_find_methods_use_object_ids_and_active_status() -> None:
    collection, _ = make_collection()
    record_id = collection.insert_one.return_value.inserted_id
    record = {"_id": record_id, "status": "active"}
    collection.find_one.side_effect = [record, record, record, record]
    repository = ParkingRepository(collection)

    created = await repository.create_record({"plate_number": "LEA-1234"})
    fetched = await repository.find_by_id(str(record_id))
    active = await repository.find_active_by_id(str(record_id))
    by_plate = await repository.find_active_by_normalized_plate("LEA1234")

    assert created == record
    assert fetched == record
    assert active == record
    assert by_plate == record
    collection.find_one.assert_any_await({"_id": record_id})
    collection.find_one.assert_any_await(
        {"_id": record_id, "status": "active"}
    )
    collection.find_one.assert_any_await(
        {"normalized_plate_number": "LEA1234", "status": "active"}
    )


@pytest.mark.asyncio
async def test_duplicate_lookup_can_exclude_current_record() -> None:
    collection, _ = make_collection()
    repository = ParkingRepository(collection)
    record_id = ObjectId()

    await repository.find_duplicate_active_plate(
        "LEA1234", exclude_id=str(record_id)
    )

    collection.find_one.assert_awaited_once_with(
        {
            "normalized_plate_number": "LEA1234",
            "status": "active",
            "_id": {"$ne": record_id},
        }
    )


@pytest.mark.asyncio
async def test_active_list_and_count_apply_filters_pagination_and_sort() -> None:
    collection, cursor = make_collection()
    repository = ParkingRepository(collection)
    filters = {"vehicle_type": "bike", "search": "LEA12"}

    await repository.list_active(filters, page=2, limit=20)
    await repository.count_active(filters)

    query = collection.find.call_args.args[0]
    assert query == {
        "status": "active",
        "vehicle_type": "bike",
        "normalized_plate_number": {"$regex": "LEA12", "$options": "i"},
    }
    cursor.sort.assert_called_once_with("entry_time", -1)
    cursor.skip.assert_called_once_with(20)
    cursor.limit.assert_called_once_with(20)
    collection.count_documents.assert_awaited_once_with(query)


@pytest.mark.asyncio
async def test_completed_history_uses_exit_time_and_excludes_deleted() -> None:
    collection, cursor = make_collection()
    repository = ParkingRepository(collection)
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 6, 30, tzinfo=timezone.utc)
    filters = {
        "status": "completed",
        "vehicle_type": "car",
        "search": "LEA",
        "start_at": start,
        "end_before": end,
    }

    await repository.list_history(filters, 1, 20)
    await repository.count_history(filters)

    query = collection.find.call_args.args[0]
    assert query["status"] == "completed"
    assert query["exit_time"] == {"$gte": start, "$lt": end}
    assert query["vehicle_type"] == "car"
    assert query["normalized_plate_number"]["$regex"] == "LEA"
    cursor.sort.assert_called_once_with("exit_time", -1)
    collection.count_documents.assert_awaited_once_with(query)


@pytest.mark.asyncio
async def test_unfiltered_history_dates_use_exit_for_completed_and_entry_otherwise() -> None:
    collection, _ = make_collection()
    repository = ParkingRepository(collection)
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 7, 1, tzinfo=timezone.utc)

    await repository.list_history(
        {"start_at": start, "end_before": end}, 1, 20
    )

    query = collection.find.call_args.args[0]
    assert query["status"] == {"$ne": "deleted"}
    assert query["$or"] == [
        {
            "status": "completed",
            "exit_time": {"$gte": start, "$lt": end},
        },
        {
            "status": {"$in": ["active", "cancelled"]},
            "entry_time": {"$gte": start, "$lt": end},
        },
    ]


@pytest.mark.asyncio
async def test_search_is_exact_and_excludes_deleted_by_default() -> None:
    collection, cursor = make_collection()
    cursor.to_list.return_value = [{"status": "active"}]
    repository = ParkingRepository(collection)

    results = await repository.search_by_plate("LEA1234")
    await repository.search_by_plate("LEA1234", status="completed")

    first_query = collection.find.call_args_list[0].args[0]
    second_query = collection.find.call_args_list[1].args[0]
    assert first_query == {
        "normalized_plate_number": "LEA1234",
        "status": {"$ne": "deleted"},
    }
    assert second_query == {
        "normalized_plate_number": "LEA1234",
        "status": "completed",
    }
    assert results == [{"status": "active"}]


@pytest.mark.asyncio
async def test_update_completion_and_soft_delete_are_atomic() -> None:
    collection, _ = make_collection()
    updated = {"_id": ObjectId(), "status": "active"}
    completed = {**updated, "status": "completed"}
    deleted = {**updated, "status": "deleted"}
    collection.find_one_and_update.side_effect = [updated, completed, deleted]
    repository = ParkingRepository(collection)
    record_id = str(updated["_id"])
    actor_id = str(ObjectId())

    assert await repository.update_record(record_id, {"slot": "A-1"}) == updated
    assert await repository.complete_exit(record_id, {"fee": 50}) == completed
    assert await repository.soft_delete_record(record_id, actor_id) == deleted

    update_calls = collection.find_one_and_update.await_args_list
    assert update_calls[0].args[0] == {
        "_id": updated["_id"],
        "status": {"$ne": "deleted"},
    }
    assert update_calls[1].args[0] == {
        "_id": updated["_id"],
        "status": "active",
    }
    assert update_calls[2].args[1]["$set"]["status"] == "deleted"
    assert update_calls[2].args[1]["$set"]["updated_by"] == ObjectId(actor_id)
    assert all(
        call.kwargs["return_document"] == ReturnDocument.AFTER
        for call in update_calls
    )
