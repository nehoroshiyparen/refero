import uuid
from pydantic import BaseModel

from ...models import ReviewStatusEnum


class CreateReviewDTO(BaseModel):
    review_assignment_id: uuid.UUID
    status: ReviewStatusEnum
