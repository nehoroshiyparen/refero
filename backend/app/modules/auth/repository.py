from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .models import RefreshToken
from .query_builder import TokenQueryBuilder

class TokenRepository(BaseRepository[RefreshToken]):
    builder_class = TokenQueryBuilder

    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)