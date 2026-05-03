from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from ..models import ReviewerProfile

class ReviewerProfileRepository(BaseRepository[ReviewerProfile]):
    def __init__(self, model, session: AsyncSession):
        super().__init__(model, session)