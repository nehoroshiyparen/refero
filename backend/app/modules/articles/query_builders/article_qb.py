from app.infrastructure.database import BaseQueryBuilder
from ..models import Article

class ArticleQueryBuilder(BaseQueryBuilder[Article]):
    def __init__(self, model):
        super().__init__(model)