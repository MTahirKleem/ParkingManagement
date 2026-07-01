from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.parking import router as parking_router
from app.api.v1.users import router as users_router
from app.database.mongodb import get_database

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(parking_router)


@api_router.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "ParkingManagement API is running",
        "data": {
            "service": "backend",
            "status": "healthy",
        },
    }


@api_router.get("/health/database")
async def database_health_check():
    database = get_database()

    await database.command("ping")

    collections = await database.list_collection_names()

    return {
        "success": True,
        "message": "MongoDB connection is healthy",
        "data": {
            "database": database.name,
            "status": "connected",
            "collections": collections,
        },
    }
