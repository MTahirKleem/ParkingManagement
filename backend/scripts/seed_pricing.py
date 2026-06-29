import asyncio
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.constants import Currencies, PricingTypes
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.repositories.pricing_repository import PricingRepository
from app.utils.datetime import utc_now


DEFAULT_PRICING = {
    "bike": {"pricing_type": PricingTypes.FIXED, "fixed_rate": 50},
    "car": {"pricing_type": PricingTypes.FIXED, "fixed_rate": 100},
}


async def seed_pricing(repository: PricingRepository) -> int:
    created_count = 0
    for vehicle_type, defaults in DEFAULT_PRICING.items():
        existing = await repository.find_active_by_vehicle_type(vehicle_type)
        if existing:
            print(f"Active {vehicle_type} pricing already exists")
            continue

        now = utc_now()
        await repository.create_pricing_rule(
            {
                "vehicle_type": vehicle_type,
                "pricing_type": defaults["pricing_type"],
                "fixed_rate": defaults["fixed_rate"],
                "base_hours": None,
                "base_fee": None,
                "extra_hour_fee": None,
                "grace_minutes": 0,
                "currency": Currencies.PKR,
                "is_active": True,
                "created_by": None,
                "updated_by": None,
                "created_at": now,
                "updated_at": now,
            }
        )
        created_count += 1
        print(f"Default {vehicle_type} pricing created successfully")
    return created_count


async def main() -> None:
    await connect_to_mongo()
    try:
        await seed_pricing(PricingRepository())
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
