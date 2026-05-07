from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from .models import User

class UserQueryBuilder(BaseQueryBuilder[User]):
    def __init__(self, model, stmt):
        super().__init__(model, stmt)

    def with_role(self):
        self._stmt = self._stmt.options(
            selectinload(self._model.role)
        )
        return self
