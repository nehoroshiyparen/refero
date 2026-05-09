from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from .models import User, RoleName
from .query_builder import UserQueryBuilder

class UserRepository(BaseRepository[User, UserQueryBuilder]):
    query_builder = UserQueryBuilder

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)