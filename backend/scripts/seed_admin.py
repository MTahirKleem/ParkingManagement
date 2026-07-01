import asyncio
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.constants import UserRoles, UserStatus
from app.core.security import hash_password
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.repositories.user_repository import UserRepository
from app.utils.datetime import utc_now


DEFAULT_ADMIN_EMAIL = "admin@parkingmanagement.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"


async def seed_admin(repository: UserRepository) -> bool:
    existing_admin = await repository.find_by_email(DEFAULT_ADMIN_EMAIL)
    if existing_admin:
        print(f"Default admin already exists: {DEFAULT_ADMIN_EMAIL}")
        return False

    now = utc_now()
    await repository.create_user(
        {
            "name": "System Admin",
            "email": DEFAULT_ADMIN_EMAIL,
            "phone": None,
            "password_hash": hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": UserRoles.ADMIN,
            "status": UserStatus.ACTIVE,
            "last_login_at": None,
            "created_by": None,
            "updated_by": None,
            "created_at": now,
            "updated_at": now,
        }
    )
    print(f"Default admin created successfully: {DEFAULT_ADMIN_EMAIL}")
    return True


async def main() -> None:
    await connect_to_mongo()
    try:
        await seed_admin(UserRepository())
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())
