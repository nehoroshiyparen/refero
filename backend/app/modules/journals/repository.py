from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .query_builder import JournalQueryBuilder
from .models import Journal

class JournalRepository(BaseRepository[Journal, JournalQueryBuilder]):
    def __init__(self, model, session: AsyncSession):
        super().__init__(model, session)