import uuid
from sqlalchemy.orm import selectinload

from app.infrastructure.database import BaseQueryBuilder
from .models import Review, ReviewStatusEnum

class ReviewQueryBuilder(BaseQueryBuilder[Review]):
    def __init__(self, model):
        super().__init__(model)

    def filter_by_article(self, article_id: uuid.UUID | None) -> "ReviewQueryBuilder":
        if article_id is not None:
            self._stmt = self._stmt.where(Review.article_id == article_id)
        return self

    def filter_by_reviewer(self, reviewer_id: uuid.UUID | None) -> "ReviewQueryBuilder":
        if reviewer_id is not None:
            self._stmt = self._stmt.where(Review.reviewer_id == reviewer_id)
        return self

    def filter_by_status(self, status: ReviewStatusEnum | None) -> "ReviewQueryBuilder":
        if status is not None:
            self._stmt = self._stmt.where(Review.status == status.value)
        return self

    def with_reviewer(self) -> "ReviewQueryBuilder":
        self._stmt = self._stmt.options(selectinload(Review.reviewer))
        return self

    def with_article(self) -> "ReviewQueryBuilder":
        self._stmt = self._stmt.options(selectinload(Review.article))
        return self
