import uuid
from pydantic import BaseModel, Field

from ..models import ReviewStatusEnum

class ReviewFiltersDTO(BaseModel):
    status: ReviewStatusEnum | None = None
    article_id: uuid.UUID | None = None

    limit: int = 10
    offset: int = 0
