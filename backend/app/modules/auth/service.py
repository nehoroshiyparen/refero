from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.base import BaseService
from app.infrastructure.database.base import SearchOptions
from app.modules.users.repositories import UserRepository, User
from app.core.exceptions import Conflict
from .repository import TokenRepository
from .schemas import (
    RegisterRequest,
    RegisterPaylaod, 
    LoginRequest
)
from .utils import (
    hash_password, 
    verify_password,
    generate_refresh_token, 
    create_access_token, 
    decode_access_token,
    hash_refresh_token,
)

class AuthService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._token_repo: TokenRepository = TokenRepository(self._session)
        self._user_repo: UserRepository = UserRepository(self._session)

    async def register(self, data: RegisterRequest) -> RegisterPaylaod:
        email_exists = await self._user_repo.search_by_filters(SearchOptions(
            filters=[User.email == data.email]
        ))
        username_exists = await self._user_repo.search_by_filters(SearchOptions(
            filters=[User.username == data.username]
        ))

        details = {}
        if email_exists:
            details["email"] = "Already taken"
        if username_exists:
            details["username"] = "Already taken"

        if details:
            raise Conflict(
                message="User already exists",
                details=details
            )

        user = await self._user_repo.create(
            data={
                **data.model_dump(exclude={"password"}),
                "hashed_password": hash_password(data.password)
            }
        )

        access_token = create_access_token(payload={"sub": str(user.id), "role": user.role_name.value})
        refresh_token = generate_refresh_token()
        
        await self._token_repo.create(
            data={
                "user_id": user.id,
                "token_hash": refresh_token.token_hash,
                "expires_at": refresh_token.expires_at
            }
        )

        return RegisterPaylaod(
            access_token=access_token,
            refresh_token=refresh_token
        )


    async def login(self, data: LoginRequest):
        pass

    async def refresh(self, refresh_token: str):
        pass

    async def logout(self, refresh_token: str):
        pass