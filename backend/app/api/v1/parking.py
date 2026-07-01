from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query, Request, status

from app.core.constants import ErrorCodes, UserRoles
from app.core.permissions import require_admin, require_roles
from app.schemas.common import AppException, SuccessResponse
from app.schemas.parking import (
    DeletedParkingResponse,
    ParkingActiveQuery,
    ParkingEntryRequest,
    ParkingExitRequest,
    ParkingHistoryQuery,
    ParkingListResponse,
    ParkingRecordResponse,
    ParkingSearchQuery,
    ParkingUpdateRequest,
    VehicleType,
    VisibleParkingStatus,
)
from app.services.parking_service import ParkingService


router = APIRouter(prefix="/parking", tags=["Parking"])
require_parking_operator = require_roles(UserRoles.ADMIN, UserRoles.GUARD)


def get_parking_service() -> ParkingService:
    return ParkingService()


def get_history_query(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: VisibleParkingStatus | None = Query(
        default=None, alias="status"
    ),
    vehicle_type: VehicleType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = Query(default=None, min_length=1),
) -> ParkingHistoryQuery:
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise AppException(
            status_code=422,
            message="start_date must not be after end_date",
            error_code=ErrorCodes.VALIDATION_ERROR,
            details={"start_date": "Must not be after end_date"},
        )
    return ParkingHistoryQuery(
        page=page,
        limit=limit,
        status=status_filter,
        vehicle_type=vehicle_type,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )


def _request_context(request: Request) -> dict[str, str | None]:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


@router.post(
    "/entry",
    response_model=SuccessResponse[ParkingRecordResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_entry(
    payload: ParkingEntryRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    data = await service.create_entry(
        payload, current_user, _request_context(request)
    )
    return {
        "success": True,
        "message": "Vehicle entry created successfully",
        "data": data,
    }


@router.post(
    "/{record_id}/exit",
    response_model=SuccessResponse[ParkingRecordResponse],
)
async def complete_exit(
    record_id: str,
    payload: ParkingExitRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    data = await service.complete_exit(
        record_id,
        payload,
        current_user,
        _request_context(request),
    )
    return {
        "success": True,
        "message": "Vehicle exit completed successfully",
        "data": data,
    }


@router.get("/active", response_model=ParkingListResponse)
async def list_active(
    query: ParkingActiveQuery = Depends(),
    _: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    result = await service.get_active_vehicles(query.model_dump())
    return {
        "success": True,
        "message": "Active vehicles fetched successfully",
        **result,
    }


@router.get("/history", response_model=ParkingListResponse)
async def list_history(
    query: ParkingHistoryQuery = Depends(get_history_query),
    _: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    result = await service.get_history(query.model_dump())
    return {
        "success": True,
        "message": "Parking history fetched successfully",
        **result,
    }


@router.get(
    "/search",
    response_model=SuccessResponse[list[ParkingRecordResponse]],
)
async def search_records(
    query: ParkingSearchQuery = Depends(),
    _: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    data = await service.search_records(
        query.plate_number, query.status
    )
    return {
        "success": True,
        "message": "Parking records found successfully",
        "data": data,
    }


@router.get(
    "/{record_id}",
    response_model=SuccessResponse[ParkingRecordResponse],
)
async def get_record(
    record_id: str,
    _: dict[str, Any] = Depends(require_parking_operator),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    return {
        "success": True,
        "message": "Parking record fetched successfully",
        "data": await service.get_record_by_id(record_id),
    }


@router.put(
    "/{record_id}",
    response_model=SuccessResponse[ParkingRecordResponse],
)
async def update_record(
    record_id: str,
    payload: ParkingUpdateRequest,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    data = await service.update_record(
        record_id,
        payload,
        current_user,
        _request_context(request),
    )
    return {
        "success": True,
        "message": "Parking record updated successfully",
        "data": data,
    }


@router.delete(
    "/{record_id}",
    response_model=SuccessResponse[DeletedParkingResponse],
)
async def delete_record(
    record_id: str,
    request: Request,
    current_user: dict[str, Any] = Depends(require_admin),
    service: ParkingService = Depends(get_parking_service),
) -> dict[str, Any]:
    data = await service.delete_record(
        record_id, current_user, _request_context(request)
    )
    return {
        "success": True,
        "message": "Parking record deleted successfully",
        "data": data,
    }
