from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from .models import User, RoleName

class UserQueryBuilder(BaseQueryBuilder[User]):
    def __init__(self, model):
        super().__init__(model)

    def extended_profile(self):
        self._stmt = self._stmt.options(
            selectinload(self._model.author_profile),
            selectinload(self._model.reviewer_profile),
        )
        return self

    def filter_by_role(self, role_name: RoleName | None) -> "UserQueryBuilder":
        if role_name is not None:
            self._stmt = self._stmt.where(User.role_name == role_name)
        return self

    def filter_text(self, query: str | None) -> "UserQueryBuilder":
        if query:
            pattern = f"%{query}%"
            self._stmt = self._stmt.where(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
        return self