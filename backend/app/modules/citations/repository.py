from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import BaseRepository

from .query_builder import CitationQueryBuilder
from .models import Citation

class CitationRepository(BaseRepository[Citation, CitationQueryBuilder]):
    _query_builder = CitationQueryBuilder
    _model = Citation

    def __init__(self, session: AsyncSession):
        super().__init__(session)