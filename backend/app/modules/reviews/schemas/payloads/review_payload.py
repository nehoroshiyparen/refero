import uuid
from datetime import datetime
from pydantic import BaseModel

from ...models import ReviewStatusEnum


class ReviewPayload(BaseModel):
    id: uuid.UUID
    review_assignment_id: uuid.UUID
    status: ReviewStatusEnum
    created_at: datetime | None = None
    completed_at: datetime | None = None
