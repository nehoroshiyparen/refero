from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from ..query_builders import ArticleApprovalsQueryBuilder
from ..models import ArticleApprovals

class ArticleApprovalsRepository(BaseRepository[ArticleApprovals, ArticleApprovalsQueryBuilder]):
    _query_builder = ArticleApprovalsQueryBuilder
    _model = ArticleApprovals

    def __init__(self, session: AsyncSession):
        super().__init__(session)