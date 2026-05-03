from pydantic import BaseModel
from typing import Any

class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Any | None = None