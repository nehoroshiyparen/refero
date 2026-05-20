from sqlalchemy.orm import selectinload
from app.infrastructure.database import BaseQueryBuilder
from ..models import ArticleApprovals

class ArticleApprovalsQueryBuilder(BaseQueryBuilder[ArticleApprovals]):
    def __init__(self, model):
        super().__init__(model)

    def with_approver(self):
        self._stmt = self._stmt.options(selectinload(ArticleApprovals.approver))
        return self