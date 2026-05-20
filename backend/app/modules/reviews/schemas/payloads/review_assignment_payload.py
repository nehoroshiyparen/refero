import uuid
from datetime import datetime
from pydantic import BaseModel

from ...models import ReviewStatusEnum


class ReviewAssignmentPayload(BaseModel):
    id: uuid.UUID
    article_version_id: uuid.UUID
    reviewer_id: uuid.UUID
    created_at: datetime


class ReviewAssignmentFullPayload(ReviewAssignmentPayload):
    review_status: ReviewStatusEnum | None = None
    review_completed_at: datetime | None = None
    article_id: uuid.UUID | None = None
    article_title: str | None = None
    version_number: int | None = None
    version_title: str | None = None
