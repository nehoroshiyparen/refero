import uuid
from pydantic import BaseModel, Field

from ..models import ReviewStatusEnum

class CreateReviewDTO(BaseModel):
    article_id: uuid.UUID
    status: ReviewStatusEnum
    comment: str | None = Field(default=None, max_length=5000)
