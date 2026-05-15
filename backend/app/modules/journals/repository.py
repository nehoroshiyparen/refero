from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .query_builder import JournalQueryBuilder
from .models import Journal

class JournalRepository(BaseRepository[Journal, JournalQueryBuilder]):
    _query_builder = JournalQueryBuilder
    _model = Journal

    def __init__(self, session: AsyncSession):
        super().__init__(session)
