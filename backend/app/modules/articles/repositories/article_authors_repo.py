from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import BaseRepository
from ..query_builders import ArticleAuthorsQueryBuilder
from ..models import ArticleAuthors

class ArticleAuthorsRepository(BaseRepository[ArticleAuthors, ArticleAuthorsQueryBuilder]):
    _query_builder = ArticleAuthorsQueryBuilder
    _model = ArticleAuthors

    def __init__(self, session: AsyncSession):
        super().__init__(session)