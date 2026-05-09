from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.base import BaseRepository, BaseQueryBuilder
from .models import AuthorProfile

class AuthorRepository(BaseRepository[AuthorProfile, BaseQueryBuilder]):
    def __init__(self, model, session: AsyncSession):
        super().__init__(model, session)