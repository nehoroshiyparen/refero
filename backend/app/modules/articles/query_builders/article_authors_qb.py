from app.infrastructure.database import BaseQueryBuilder
from ..models import ArticleAuthors

class ArticleAuthorsQueryBuilder(BaseQueryBuilder[ArticleAuthors]):
    def __init__(self, model):
        super().__init__(model)