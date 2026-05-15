from typing import Generic, TypeVar, Any
from pydantic import BaseModel

DataT = TypeVar("DataT")

class SuccessResponse(BaseModel, Generic[DataT]):
    message: str | None = None
    data: DataT | None = None
    meta: Any | None = None