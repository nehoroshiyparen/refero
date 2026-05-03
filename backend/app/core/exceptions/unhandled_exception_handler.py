from fastapi import Request
from fastapi.responses import JSONResponse
from ..responses import ErrorResponse

async def unhandled_exception_handler(request: Request, e: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR"
        ).model_dump(exclude_none=True)
    )