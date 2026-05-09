

from app.core.base import BaseService

from .repository import UserRepository, User

from app.modules.auth.schemas import AccessTokenPayload

class UserService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._user_repo = UserRepository(self._session)

    async def get_user(
        self, 
        access_token_payload: AccessTokenPayload
    ) -> any:
        user = await self._user_repo.query() \
            .where(User.id == access_token_payload.id) \
            .extended_profile(role=access_token_payload.role)