from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "ParkingManagement API is running",
        "data": {
            "service": "backend",
            "status": "healthy"
        }
    }