from copy import deepcopy
from typing import Any, Iterable

from bson import ObjectId


def is_valid_object_id(value: Any) -> bool:
    return ObjectId.is_valid(value)


def to_object_id(value: Any) -> ObjectId:
    if not is_valid_object_id(value):
        raise ValueError("Invalid ObjectId")
    return ObjectId(value)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {
            ("id" if key == "_id" else key): _serialize_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_serialize_value(item) for item in value)
    return value


def serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    return _serialize_value(deepcopy(document))


def object_id_to_str(document: dict[str, Any]) -> dict[str, Any]:
    return serialize_document(document)


def serialize_documents(
    documents: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [serialize_document(document) for document in documents]
