from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .query_builder import TokenQueryBuilder
from .models import RefreshToken

class TokenRepository(BaseRepository[RefreshToken, TokenQueryBuilder]):
    _query_builder = TokenQueryBuilder
    _model = RefreshToken

    def __init__(self, session: AsyncSession):
        super().__init__(session)