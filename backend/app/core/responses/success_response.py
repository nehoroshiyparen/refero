from pydantic import BaseModel
from typing import Any

class SuccessResponse(BaseModel):
    message: str | None = None
    data: Any | None = None
    meta: Any | None = None