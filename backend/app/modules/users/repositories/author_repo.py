import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from ..models import AuthorProfile


class AuthorRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_user_id(self, user_id: uuid.UUID) -> AuthorProfile | None:
        stmt = select(AuthorProfile).where(AuthorProfile.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, data: dict) -> None:
        data["user_id"] = user_id
        stmt = insert(AuthorProfile).values(**data).on_conflict_do_update(
            index_elements=["user_id"],
            set_=data,
        )
        await self._session.execute(stmt)
