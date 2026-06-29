from datetime import date, datetime
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.core.constants import (
    Currencies,
    ParkingStatus,
    PaymentMethods,
    VehicleTypes,
)
from app.schemas.common import PaginatedResponse
from app.schemas.pricing import PricingSnapshotResponse


VisibleParkingStatus = Literal[
    ParkingStatus.ACTIVE,
    ParkingStatus.COMPLETED,
    ParkingStatus.CANCELLED,
]
VehicleType = Literal[VehicleTypes.BIKE, VehicleTypes.CAR]


class ParkingEntryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    plate_number: str = Field(min_length=1)
    vehicle_type: VehicleType
    slot: str | None = None


class ParkingExitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_received: Literal[True]


class ParkingUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    plate_number: str | None = Field(default=None, min_length=1)
    vehicle_type: VehicleType | None = None
    slot: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def require_update_field(self) -> "ParkingUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one update field is required")
        return self


class PaymentResponse(BaseModel):
    method: Literal[PaymentMethods.CASH]
    received: bool
    received_by: str
    received_at: datetime


class ParkingRecordResponse(BaseModel):
    id: str
    plate_number: str
    normalized_plate_number: str
    vehicle_type: VehicleType
    slot: str | None = None
    entry_time: datetime
    exit_time: datetime | None = None
    status: VisibleParkingStatus
    duration_minutes: int | None = None
    fee: float | int | None = None
    currency: Literal[Currencies.PKR]
    payment: PaymentResponse | None = None
    pricing_snapshot: PricingSnapshotResponse | None = None
    ocr: dict[str, Any] | None = None
    notes: str | None = None
    created_by: str
    completed_by: str | None = None
    updated_by: str | None = None
    created_at: datetime
    updated_at: datetime


class ParkingListResponse(PaginatedResponse[ParkingRecordResponse]):
    pass


class DeletedParkingResponse(BaseModel):
    id: str
    status: Literal[ParkingStatus.DELETED]


class ParkingActiveQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    search: str | None = Field(default=None, min_length=1)
    vehicle_type: VehicleType | None = None


class ParkingHistoryQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    status: VisibleParkingStatus | None = None
    vehicle_type: VehicleType | None = None
    start_date: date | None = None
    end_date: date | None = None
    search: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_date_range(self) -> "ParkingHistoryQuery":
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("start_date must not be after end_date")
        return self


class ParkingSearchQuery(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    plate_number: str = Field(min_length=1)
    status: VisibleParkingStatus | None = None
