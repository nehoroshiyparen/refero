from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from ..responses import ErrorResponse

async def http_exception_handler(request: Request, e: HTTPException):
    return JSONResponse(
        status_code=e.status_code,
        content=ErrorResponse(
            error=str(e.detail),
            code="HTTP_ERROR"
        ).model_dump()
    )