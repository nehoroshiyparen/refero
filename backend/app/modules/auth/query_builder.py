from typing import Self
from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from .models import RefreshToken

class TokenQueryBuilder(BaseQueryBuilder[RefreshToken]):
    def __init__(self, model):
        super().__init__(model)

    def with_user(self) -> Self:
        self._stmt = self._stmt.options(
            selectinload(self._model.user)
        )
        return self