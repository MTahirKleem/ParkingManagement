from datetime import date, datetime, time, timedelta, timezone
from math import ceil
from typing import Any

from pymongo.errors import DuplicateKeyError

from app.core.constants import (
    AuditActions,
    Currencies,
    ErrorCodes,
    ParkingStatus,
    PaymentMethods,
)
from app.repositories.parking_repository import ParkingRepository
from app.schemas.common import AppException
from app.schemas.parking import (
    ParkingEntryRequest,
    ParkingExitRequest,
    ParkingUpdateRequest,
)
from app.services.audit_log_service import AuditLogService
from app.services.pricing_service import PricingService
from app.utils.datetime import utc_now
from app.utils.object_id import is_valid_object_id, serialize_document
from app.utils.plate import normalize_plate_number


class ParkingService:
    def __init__(
        self,
        parking_repository: ParkingRepository | None = None,
        pricing_service: PricingService | None = None,
        audit_log_service: AuditLogService | None = None,
    ) -> None:
        self.parking_repository = (
            parking_repository
            if parking_repository is not None
            else ParkingRepository()
        )
        self.pricing_service = (
            pricing_service
            if pricing_service is not None
            else PricingService()
        )
        self.audit_log_service = (
            audit_log_service
            if audit_log_service is not None
            else AuditLogService()
        )

    @staticmethod
    def _validate_id(record_id: str) -> None:
        if not is_valid_object_id(record_id):
            raise AppException(
                status_code=400,
                message="Invalid parking record ID",
                error_code=ErrorCodes.VALIDATION_ERROR,
                details={"record_id": "Must be a valid ObjectId"},
            )

    @staticmethod
    def _not_found() -> AppException:
        return AppException(
            status_code=404,
            message="Parking record not found",
            error_code=ErrorCodes.PARKING_RECORD_NOT_FOUND,
        )

    @staticmethod
    def _duplicate() -> AppException:
        return AppException(
            status_code=409,
            message="An active vehicle with this plate already exists",
            error_code=ErrorCodes.DUPLICATE_ACTIVE_VEHICLE,
        )

    async def _get_visible_record(
        self, record_id: str
    ) -> dict[str, Any]:
        self._validate_id(record_id)
        record = await self.parking_repository.find_by_id(record_id)
        if not record or record.get("status") == ParkingStatus.DELETED:
            raise self._not_found()
        return record

    async def create_entry(
        self,
        request_data: ParkingEntryRequest,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        plate_number = request_data.plate_number.upper()
        normalized = normalize_plate_number(plate_number)
        if not normalized:
            raise AppException(
                status_code=422,
                message="Plate number must contain letters or numbers",
                error_code=ErrorCodes.VALIDATION_ERROR,
            )
        if await self.parking_repository.find_duplicate_active_plate(
            normalized
        ):
            raise self._duplicate()

        now = utc_now()
        document = {
            "plate_number": plate_number,
            "normalized_plate_number": normalized,
            "vehicle_type": request_data.vehicle_type,
            "slot": request_data.slot,
            "entry_time": now,
            "exit_time": None,
            "status": ParkingStatus.ACTIVE,
            "duration_minutes": None,
            "fee": None,
            "currency": Currencies.PKR,
            "payment": None,
            "pricing_snapshot": None,
            "ocr": None,
            "notes": None,
            "created_by": current_user["_id"],
            "completed_by": None,
            "updated_by": None,
            "created_at": now,
            "updated_at": now,
        }
        try:
            record = await self.parking_repository.create_record(document)
        except DuplicateKeyError as exc:
            raise self._duplicate() from exc

        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.VEHICLE_ENTRY_CREATED,
            entity="parking_record",
            entity_id=record["_id"],
            message=f"Vehicle entry created for {record['plate_number']}",
            metadata={
                "plate_number": record["plate_number"],
                "vehicle_type": record["vehicle_type"],
                "slot": record.get("slot"),
            },
            request_context=request_context,
        )
        return serialize_document(record)

    async def complete_exit(
        self,
        record_id: str,
        request_data: ParkingExitRequest,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        record = await self._get_visible_record(record_id)
        if record["status"] == ParkingStatus.COMPLETED:
            raise AppException(
                status_code=409,
                message="Vehicle parking is already completed",
                error_code=ErrorCodes.VEHICLE_ALREADY_COMPLETED,
            )
        if record["status"] != ParkingStatus.ACTIVE:
            raise AppException(
                status_code=409,
                message="Parking record is not active",
                error_code=ErrorCodes.VEHICLE_ALREADY_COMPLETED,
            )

        exit_time = utc_now()
        pricing = await self.pricing_service.calculate_fee(
            record["vehicle_type"],
            record["entry_time"],
            exit_time,
        )
        update = {
            "exit_time": exit_time,
            "status": ParkingStatus.COMPLETED,
            "duration_minutes": pricing["duration_minutes"],
            "fee": pricing["fee"],
            "currency": pricing["currency"],
            "payment": {
                "method": PaymentMethods.CASH,
                "received": request_data.payment_received,
                "received_by": current_user["_id"],
                "received_at": exit_time,
            },
            "pricing_snapshot": pricing["pricing_snapshot"],
            "completed_by": current_user["_id"],
            "updated_at": exit_time,
        }
        completed = await self.parking_repository.complete_exit(
            record_id, update
        )
        if completed is None:
            latest = await self.parking_repository.find_by_id(record_id)
            if latest and latest.get("status") == ParkingStatus.COMPLETED:
                raise AppException(
                    status_code=409,
                    message="Vehicle parking is already completed",
                    error_code=ErrorCodes.VEHICLE_ALREADY_COMPLETED,
                )
            raise self._not_found()

        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.VEHICLE_EXIT_COMPLETED,
            entity="parking_record",
            entity_id=completed["_id"],
            message=f"Vehicle exit completed for {completed['plate_number']}",
            metadata={
                "plate_number": completed["plate_number"],
                "vehicle_type": completed["vehicle_type"],
                "duration_minutes": completed["duration_minutes"],
                "fee": completed["fee"],
                "payment_method": PaymentMethods.CASH,
            },
            request_context=request_context,
        )
        return serialize_document(completed)

    @staticmethod
    def _list_result(
        records: list[dict[str, Any]],
        page: int,
        limit: int,
        total: int,
    ) -> dict[str, Any]:
        return {
            "data": [serialize_document(record) for record in records],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": ceil(total / limit) if total else 0,
            },
        }

    async def get_active_vehicles(
        self, filters: dict[str, Any]
    ) -> dict[str, Any]:
        page = filters.get("page", 1)
        limit = filters.get("limit", 20)
        repository_filters = {
            "vehicle_type": filters.get("vehicle_type"),
            "search": (
                normalize_plate_number(filters["search"])
                if filters.get("search")
                else None
            ),
        }
        records = await self.parking_repository.list_active(
            repository_filters, page, limit
        )
        total = await self.parking_repository.count_active(
            repository_filters
        )
        return self._list_result(records, page, limit, total)

    @staticmethod
    def _utc_start(value: date) -> datetime:
        return datetime.combine(value, time.min, tzinfo=timezone.utc)

    async def get_history(
        self, filters: dict[str, Any]
    ) -> dict[str, Any]:
        page = filters.get("page", 1)
        limit = filters.get("limit", 20)
        repository_filters = {
            "status": filters.get("status"),
            "vehicle_type": filters.get("vehicle_type"),
            "search": (
                normalize_plate_number(filters["search"])
                if filters.get("search")
                else None
            ),
            "start_at": (
                self._utc_start(filters["start_date"])
                if filters.get("start_date")
                else None
            ),
            "end_before": (
                self._utc_start(filters["end_date"]) + timedelta(days=1)
                if filters.get("end_date")
                else None
            ),
        }
        records = await self.parking_repository.list_history(
            repository_filters, page, limit
        )
        total = await self.parking_repository.count_history(
            repository_filters
        )
        return self._list_result(records, page, limit, total)

    async def search_records(
        self, plate_number: str, status: str | None
    ) -> list[dict[str, Any]]:
        normalized = normalize_plate_number(plate_number)
        records = await self.parking_repository.search_by_plate(
            normalized, status
        )
        return [serialize_document(record) for record in records]

    async def get_record_by_id(self, record_id: str) -> dict[str, Any]:
        return serialize_document(
            await self._get_visible_record(record_id)
        )

    async def update_record(
        self,
        record_id: str,
        request_data: ParkingUpdateRequest,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        record = await self._get_visible_record(record_id)
        updates = request_data.model_dump(exclude_unset=True)
        if "plate_number" in updates:
            updates["plate_number"] = updates["plate_number"].upper()
            normalized = normalize_plate_number(updates["plate_number"])
            if not normalized:
                raise AppException(
                    status_code=422,
                    message="Plate number must contain letters or numbers",
                    error_code=ErrorCodes.VALIDATION_ERROR,
                )
            updates["normalized_plate_number"] = normalized
            if (
                record["status"] == ParkingStatus.ACTIVE
                and await self.parking_repository.find_duplicate_active_plate(
                    normalized, exclude_id=record_id
                )
            ):
                raise self._duplicate()

        updates["updated_by"] = current_user["_id"]
        updates["updated_at"] = utc_now()
        try:
            updated = await self.parking_repository.update_record(
                record_id, updates
            )
        except DuplicateKeyError as exc:
            raise self._duplicate() from exc
        if updated is None:
            raise self._not_found()

        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.PARKING_RECORD_UPDATED,
            entity="parking_record",
            entity_id=updated["_id"],
            message=f"Parking record updated for {updated['plate_number']}",
            metadata={
                "plate_number": updated["plate_number"],
                "updated_fields": sorted(request_data.model_fields_set),
            },
            request_context=request_context,
        )
        return serialize_document(updated)

    async def delete_record(
        self,
        record_id: str,
        current_user: dict[str, Any],
        request_context: dict[str, Any] | None,
    ) -> dict[str, str]:
        record = await self._get_visible_record(record_id)
        deleted = await self.parking_repository.soft_delete_record(
            record_id, str(current_user["_id"])
        )
        if deleted is None:
            raise self._not_found()
        await self.audit_log_service.log_action(
            user=current_user,
            action=AuditActions.PARKING_RECORD_DELETED,
            entity="parking_record",
            entity_id=record["_id"],
            message=f"Parking record deleted for {record['plate_number']}",
            metadata={"plate_number": record["plate_number"]},
            request_context=request_context,
        )
        return {"id": str(deleted["_id"]), "status": deleted["status"]}
