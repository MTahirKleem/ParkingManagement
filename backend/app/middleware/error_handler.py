from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.constants import ErrorCodes
from app.schemas.common import AppException


def _error_payload(
    message: str,
    error_code: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details or {},
    }


async def app_exception_handler(
    _: Request,
    exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.message, exc.error_code, exc.details),
    )


async def validation_exception_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = [
        {
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            "Request validation failed",
            ErrorCodes.VALIDATION_ERROR,
            {"errors": errors},
        ),
    )


async def http_exception_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    error_code = (
        ErrorCodes.UNAUTHORIZED
        if exc.status_code == 401
        else ErrorCodes.FORBIDDEN
        if exc.status_code == 403
        else ErrorCodes.VALIDATION_ERROR
        if exc.status_code in {400, 422}
        else "HTTP_ERROR"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(str(exc.detail), error_code),
        headers=exc.headers,
    )


async def unhandled_exception_handler(
    _: Request,
    __: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_error_payload(
            "Internal server error",
            ErrorCodes.INTERNAL_SERVER_ERROR,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
