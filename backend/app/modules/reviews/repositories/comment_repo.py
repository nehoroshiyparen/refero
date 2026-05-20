from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.database import BaseRepository
from app.infrastructure.database.base import BaseQueryBuilder
from ..models import VersionComment


class VersionCommentQueryBuilder(BaseQueryBuilder[VersionComment]):
    def order_by(self, *columns) -> Self:
        self._stmt = self._stmt.order_by(*columns)
        return self

    def with_user(self) -> Self:
        self._stmt = self._stmt.options(selectinload(VersionComment.user))
        return self


class VersionCommentRepository(BaseRepository[VersionComment, VersionCommentQueryBuilder]):
    _query_builder = VersionCommentQueryBuilder
    _model = VersionComment

    def __init__(self, session: AsyncSession):
        super().__init__(session)
