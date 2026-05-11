from app.infrastructure.database import BaseQueryBuilder
from ..models import ArticleApprovals

class ArticleApprovalsQueryBuilder(BaseQueryBuilder[ArticleApprovals]):
    def __init__(self, model):
        super().__init__(model)