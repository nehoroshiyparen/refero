from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.database import BaseRepository
from app.infrastructure.database.base import BaseQueryBuilder
from ..models import ReviewAssignment, Review


class ReviewAssignmentQueryBuilder(BaseQueryBuilder[ReviewAssignment]):
    def filter_by_reviewer(self, reviewer_id) -> "ReviewAssignmentQueryBuilder":
        if reviewer_id is not None:
            self._stmt = self._stmt.where(ReviewAssignment.reviewer_id == reviewer_id)
        return self

    def filter_by_version(self, version_id) -> "ReviewAssignmentQueryBuilder":
        if version_id is not None:
            self._stmt = self._stmt.where(ReviewAssignment.article_version_id == version_id)
        return self

    def with_review(self) -> "ReviewAssignmentQueryBuilder":
        self._stmt = self._stmt.options(selectinload(ReviewAssignment.review))
        return self

    def with_article_version(self) -> "ReviewAssignmentQueryBuilder":
        self._stmt = self._stmt.options(selectinload(ReviewAssignment.article_version))
        return self


class ReviewAssignmentRepository(BaseRepository[ReviewAssignment, ReviewAssignmentQueryBuilder]):
    _query_builder = ReviewAssignmentQueryBuilder
    _model = ReviewAssignment

    def __init__(self, session: AsyncSession):
        super().__init__(session)
