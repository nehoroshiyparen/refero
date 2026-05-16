from sqlalchemy.orm import selectinload

from app.infrastructure.database import BaseQueryBuilder
from .models import Review, ReviewStatusEnum


class ReviewQueryBuilder(BaseQueryBuilder[Review]):
    def filter_by_assignment(self, assignment_id) -> "ReviewQueryBuilder":
        if assignment_id is not None:
            self._stmt = self._stmt.where(Review.review_assignment_id == assignment_id)
        return self

    def filter_by_status(self, status: ReviewStatusEnum | None) -> "ReviewQueryBuilder":
        if status is not None:
            self._stmt = self._stmt.where(Review.status == status.value)
        return self
