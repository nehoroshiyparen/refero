from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from app.infrastructure.database import BaseRepository
from app.infrastructure.database.base import BaseQueryBuilder
from ..models import ArticleVersion, ArticleStatus
from ..models.article_approvals import ArticleApprovals
from ..models.enum import ApprovalStatus

class ArticleVersionQueryBuilder(BaseQueryBuilder[ArticleVersion]):
    def order_by(self, *columns) -> Self:
        self._stmt = self._stmt.order_by(*columns)
        return self

    def filter_status(self, status: ArticleStatus | None) -> Self:
        if status is not None:
            self._stmt = self._stmt.where(ArticleVersion.status == status.value)
        return self

    def filter_by_statuses(self, statuses: list[ArticleStatus] | None) -> Self:
        if statuses:
            self._stmt = self._stmt.where(
                ArticleVersion.status.in_([s.value for s in statuses])
            )
        return self

    def filter_approved_only(self, approved: bool = False) -> Self:
        if approved:
            subq = (
                select(ArticleApprovals.id)
                .where(
                    ArticleApprovals.article_version_id == ArticleVersion.id,
                    ArticleApprovals.status != ApprovalStatus.APPROVED.value,
                )
                .correlate(ArticleVersion)
            )
            self._stmt = self._stmt.where(~exists(subq))
        return self


class ArticleVersionRepository(BaseRepository[ArticleVersion, ArticleVersionQueryBuilder]):
    _query_builder = ArticleVersionQueryBuilder
    _model = ArticleVersion

    def __init__(self, session: AsyncSession):
        super().__init__(session)
