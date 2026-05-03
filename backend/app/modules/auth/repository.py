from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .models import RefreshToken

class TokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)