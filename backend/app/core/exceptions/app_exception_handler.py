from fastapi import Request
from fastapi.responses import JSONResponse
from .types import AppException
from ..responses import ErrorResponse

async def app_exception_handler(request: Request, e: AppException):
    return JSONResponse(
        status_code=e.status_code,
        content=ErrorResponse(
            error=e.message,
            code=e.code,
            details=e.details
        ).model_dump()
    )