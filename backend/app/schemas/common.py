from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str
    data: DataT


class Pagination(BaseModel):
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    pages: int = Field(ge=0)


class PaginatedResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str
    data: list[DataT]
    pagination: Pagination


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: dict[str, Any] = Field(default_factory=dict)


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)
