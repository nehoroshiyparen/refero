import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.infrastructure.database import BaseRepository
from .models import User, RoleName, AuthorProfile, ReviewerProfile
from .query_builder import UserQueryBuilder

class UserRepository(BaseRepository[User, UserQueryBuilder]):
    _query_builder = UserQueryBuilder
    _model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def upsert_author_profile(self, user_id: uuid.UUID, data: dict) -> None:
        data["user_id"] = user_id
        stmt = insert(AuthorProfile).values(**data).on_conflict_do_update(
            index_elements=["user_id"],
            set_=data,
        )
        await self._session.execute(stmt)

    async def upsert_reviewer_profile(self, user_id: uuid.UUID, data: dict) -> None:
        data["user_id"] = user_id
        stmt = insert(ReviewerProfile).values(**data).on_conflict_do_update(
            index_elements=["user_id"],
            set_=data,
        )
        await self._session.execute(stmt)
