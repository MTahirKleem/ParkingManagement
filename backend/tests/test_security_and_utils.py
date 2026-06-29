from datetime import datetime, timezone

import pytest
from bson import ObjectId
from jose import ExpiredSignatureError

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.utils.datetime import utc_now
from app.utils.object_id import (
    is_valid_object_id,
    object_id_to_str,
    serialize_document,
    serialize_documents,
    to_object_id,
)


def test_password_hash_round_trip() -> None:
    hashed = hash_password("Admin@123")

    assert hashed != "Admin@123"
    assert verify_password("Admin@123", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_access_token_contains_subject_role_and_expiration() -> None:
    token = create_access_token({"sub": "507f1f77bcf86cd799439011", "role": "admin"})

    payload = decode_access_token(token)

    assert payload["sub"] == "507f1f77bcf86cd799439011"
    assert payload["role"] == "admin"
    assert isinstance(payload["exp"], int)


def test_expired_access_token_is_rejected() -> None:
    from datetime import timedelta

    token = create_access_token(
        {"sub": "507f1f77bcf86cd799439011", "role": "guard"},
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_utc_now_returns_timezone_aware_utc_datetime() -> None:
    result = utc_now()

    assert result.tzinfo is not None
    assert result.utcoffset() == timezone.utc.utcoffset(result)


def test_object_id_helpers_validate_and_convert() -> None:
    value = "507f1f77bcf86cd799439011"

    assert is_valid_object_id(value) is True
    assert is_valid_object_id("invalid") is False
    assert to_object_id(value) == ObjectId(value)

    with pytest.raises(ValueError):
        to_object_id("invalid")


def test_document_serialization_renames_id_and_converts_nested_values() -> None:
    user_id = ObjectId()
    document = {
        "_id": user_id,
        "created_by": user_id,
        "nested": {"entity_id": user_id},
        "items": [{"user_id": user_id}],
        "created_at": datetime(2026, 6, 29, tzinfo=timezone.utc),
    }

    result = serialize_document(document)

    assert result["id"] == str(user_id)
    assert "_id" not in result
    assert result["created_by"] == str(user_id)
    assert result["nested"]["entity_id"] == str(user_id)
    assert result["items"][0]["user_id"] == str(user_id)
    assert document["_id"] == user_id


def test_object_id_to_str_and_document_list_serialization() -> None:
    first = {"_id": ObjectId(), "name": "First"}
    second = {"_id": ObjectId(), "name": "Second"}

    converted = object_id_to_str(first)
    results = serialize_documents([first, second])

    assert converted["id"] == str(first["_id"])
    assert [result["name"] for result in results] == ["First", "Second"]
