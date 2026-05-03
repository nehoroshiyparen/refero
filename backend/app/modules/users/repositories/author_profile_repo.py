from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from ..models import AuthorProfile

class AuthorProfileRepository(BaseRepository[AuthorProfile]):
    def __init__(self, model, session: AsyncSession):
        super().__init__(model, session)