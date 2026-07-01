import re
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository_normalizes_email_and_inserts_user() -> None:
    collection = MagicMock()
    collection.find_one = AsyncMock(side_effect=[None, {"_id": ObjectId(), "email": "guard@example.com"}])
    collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))
    )
    repository = UserRepository(collection)

    await repository.find_by_email(" GUARD@EXAMPLE.COM ")
    created = await repository.create_user({"email": "guard@example.com"})

    collection.find_one.assert_any_await({"email": "guard@example.com"})
    collection.insert_one.assert_awaited_once_with({"email": "guard@example.com"})
    assert created["email"] == "guard@example.com"


@pytest.mark.asyncio
async def test_user_repository_lists_with_filters_search_and_pagination() -> None:
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[{"name": "Ali"}])
    collection = MagicMock()
    collection.find.return_value = cursor
    collection.count_documents = AsyncMock(return_value=1)
    repository = UserRepository(collection)

    users = await repository.list_users(
        {"role": "guard", "status": "active", "search": "a.li"},
        page=2,
        limit=20,
    )
    total = await repository.count_users({"search": "a.li"})

    query = collection.find.call_args.args[0]
    assert query["role"] == "guard"
    assert query["status"] == "active"
    assert query["$or"][0]["name"]["$regex"] == re.escape("a.li")
    cursor.skip.assert_called_once_with(20)
    cursor.limit.assert_called_once_with(20)
    assert users == [{"name": "Ali"}]
    assert total == 1


@pytest.mark.asyncio
async def test_user_repository_finds_names_for_ids_in_one_query() -> None:
    first_id = ObjectId()
    second_id = ObjectId()
    cursor = MagicMock()
    cursor.to_list = AsyncMock(
        return_value=[
            {"_id": first_id, "name": "Entry Guard"},
            {"_id": second_id, "name": "Exit Guard"},
        ]
    )
    collection = MagicMock()
    collection.find.return_value = cursor
    repository = UserRepository(collection)

    result = await repository.find_names_by_ids(
        {str(first_id), str(second_id)}
    )

    query, projection = collection.find.call_args.args
    assert set(query["_id"]["$in"]) == {first_id, second_id}
    assert projection == {"name": 1}
    assert result == {
        str(first_id): "Entry Guard",
        str(second_id): "Exit Guard",
    }


@pytest.mark.asyncio
async def test_audit_repository_only_inserts_and_lists_logs() -> None:
    collection = MagicMock()
    collection.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id=ObjectId("507f1f77bcf86cd799439011"))
    )
    collection.find_one = AsyncMock(return_value={"_id": ObjectId(), "action": "USER_CREATED"})
    cursor = MagicMock()
    cursor.sort.return_value = cursor
    cursor.skip.return_value = cursor
    cursor.limit.return_value = cursor
    cursor.to_list = AsyncMock(return_value=[])
    collection.find.return_value = cursor
    collection.count_documents = AsyncMock(return_value=0)
    repository = AuditLogRepository(collection)

    created = await repository.create_log({"action": "USER_CREATED"})
    listed = await repository.list_logs({"action": "USER_CREATED"}, 1, 20)
    count = await repository.count_logs({"action": "USER_CREATED"})

    assert created["action"] == "USER_CREATED"
    assert listed == []
    assert count == 0
    assert not hasattr(repository, "update_log")
    assert not hasattr(repository, "delete_log")
