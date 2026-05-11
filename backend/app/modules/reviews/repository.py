from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.base import BaseRepository, BaseQueryBuilder
from .models import ReviewerProfile

class ReviewerProfileRepository(BaseRepository[ReviewerProfile, BaseQueryBuilder]):
    def __init__(self, model, session: AsyncSession):
        super().__init__(model, session)