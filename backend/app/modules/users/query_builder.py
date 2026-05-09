from sqlalchemy.orm import selectinload
from app.infrastructure.database.base import BaseQueryBuilder
from .models import User, RoleName

class UserQueryBuilder(BaseQueryBuilder[User]):
    def __init__(self, model):
        super().__init__(model)

    def extended_profile(self, role: RoleName):
        if role == RoleName.GUEST:
            return self
        
        option = (
            self._model.author_profile
            if role == RoleName.AUTHOR
            else self._model.reviewer_profile
        )

        self._stmt = self._stmt.options(
            selectinload(option)
        )

        return self