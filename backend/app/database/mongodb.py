from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.core.constants import Collections


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    mongodb.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongodb.database = mongodb.client[settings.MONGO_DB_NAME]

    await mongodb.client.admin.command("ping")

    await create_indexes()


async def close_mongo_connection() -> None:
    if mongodb.client:
        mongodb.client.close()


def get_database() -> AsyncIOMotorDatabase:
    if mongodb.database is None:
        raise RuntimeError("MongoDB database is not initialized")

    return mongodb.database


def get_collection(collection_name: str):
    database = get_database()
    return database[collection_name]


async def create_indexes() -> None:
    database = get_database()

    await database[Collections.USERS].create_index(
        [("email", 1)],
        unique=True,
        name="idx_users_email_unique",
    )

    await database[Collections.USERS].create_index(
        [("role", 1)],
        name="idx_users_role",
    )

    await database[Collections.USERS].create_index(
        [("status", 1)],
        name="idx_users_status",
    )

    await database[Collections.USERS].create_index(
        [("created_at", -1)],
        name="idx_users_created_at",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("normalized_plate_number", 1)],
        name="idx_parking_normalized_plate_number",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("status", 1)],
        name="idx_parking_status",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("vehicle_type", 1)],
        name="idx_parking_vehicle_type",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("entry_time", -1)],
        name="idx_parking_entry_time",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("exit_time", -1)],
        name="idx_parking_exit_time",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("created_by", 1)],
        name="idx_parking_created_by",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("completed_by", 1)],
        name="idx_parking_completed_by",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("payment.received", 1)],
        name="idx_parking_payment_received",
    )

    await database[Collections.PARKING_RECORDS].create_index(
        [("normalized_plate_number", 1), ("status", 1)],
        unique=True,
        partialFilterExpression={"status": "active"},
        name="idx_unique_active_plate",
    )

    await database[Collections.PRICING_RULES].create_index(
        [("vehicle_type", 1)],
        name="idx_pricing_vehicle_type",
    )

    await database[Collections.PRICING_RULES].create_index(
        [("is_active", 1)],
        name="idx_pricing_is_active",
    )

    await database[Collections.PRICING_RULES].create_index(
        [("vehicle_type", 1), ("is_active", 1)],
        name="idx_pricing_vehicle_type_active",
    )

    await database[Collections.SETTINGS].create_index(
        [("parking_name", 1)],
        name="idx_settings_parking_name",
    )

    await database[Collections.AUDIT_LOGS].create_index(
        [("user_id", 1)],
        name="idx_audit_user_id",
    )

    await database[Collections.AUDIT_LOGS].create_index(
        [("action", 1)],
        name="idx_audit_action",
    )

    await database[Collections.AUDIT_LOGS].create_index(
        [("entity", 1), ("entity_id", 1)],
        name="idx_audit_entity",
    )

    await database[Collections.AUDIT_LOGS].create_index(
        [("created_at", -1)],
        name="idx_audit_created_at",
    )