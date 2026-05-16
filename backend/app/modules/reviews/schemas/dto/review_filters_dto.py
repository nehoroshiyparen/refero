from pydantic import BaseModel, Field

from ...models import ReviewStatusEnum


class ReviewFiltersDTO(BaseModel):
    status: ReviewStatusEnum | None = None

    limit: int = 10
    offset: int = 0
