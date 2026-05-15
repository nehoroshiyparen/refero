import uuid
from datetime import datetime
from pydantic import BaseModel

from ..models import ReviewStatusEnum

class ReviewPayload(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    reviewer_id: uuid.UUID
    status: ReviewStatusEnum
    comment: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None
