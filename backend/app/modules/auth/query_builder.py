from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from .models import RefreshToken

class TokenQueryBuilder(BaseQueryBuilder[RefreshToken]):
    def with_user(self):
        self._stmt = self._stmt.options(
            selectinload(self._model.user)
        )
        return self
