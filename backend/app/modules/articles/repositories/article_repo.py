from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from ..query_builders import ArticleQueryBuilder
from ..models import Article

class ArticleRepository(BaseRepository[Article, ArticleQueryBuilder]):
    _query_builder = ArticleQueryBuilder
    _model = Article

    def __init__(self, session: AsyncSession):
        super().__init__(session)