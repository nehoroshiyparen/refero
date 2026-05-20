from typing import Self
from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from app.modules.users.models import User
from .models import RefreshToken

class TokenQueryBuilder(BaseQueryBuilder[RefreshToken]):
    def __init__(self, model):
        super().__init__(model)

    def with_user(self) -> Self:
        self._stmt = self._stmt.options(
            selectinload(RefreshToken.user).selectinload(User.user_roles)
        )
        return self