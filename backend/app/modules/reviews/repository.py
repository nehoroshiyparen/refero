import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.base import BaseRepository, BaseQueryBuilder
from .models import Review
from .query_builder import ReviewQueryBuilder

class ReviewRepository(BaseRepository[Review, ReviewQueryBuilder]):
    _query_builder = ReviewQueryBuilder
    _model = Review

    def __init__(self, session: AsyncSession):
        super().__init__(session)
