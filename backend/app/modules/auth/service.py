from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.core.base import BaseService
from app.infrastructure.database.base import SearchOptions
from app.modules.users.repositories import UserRepository, User
from .repository import TokenRepository, RefreshToken
from app.core.exceptions import (
    Conflict,
    NotFound,
    Unauthorized,
)
from .schemas import (
    RegisterDTO,
    AuthorizationPaylaod, 
    LoginDTO
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

    async def register(self, data: RegisterDTO) -> AuthorizationPaylaod:
        email_exists = await self._user_repo.get_one_by_filters(SearchOptions(
            filters=[User.email == data.email]
        ))
        username_exists = await self._user_repo.get_one_by_filters(SearchOptions(
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
        
        print("ПИЗДА КОРОВЫ И БЛЯДСКИЕ УШИ", data.password)

        user = await self._user_repo.create(
            data={
                **data.model_dump(exclude={"password"}),
                "hashed_password": hash_password(data.password),
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

        return AuthorizationPaylaod(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def login(self, data: LoginDTO) -> AuthorizationPaylaod:
        filters = []

        if data.username:
            filters.append(User.username == data.username)
        if data.email:
            filters.append(User.email == data.email)

        user = await self._user_repo.get_one_by_filters(SearchOptions(
            filters=filters
        ))
        if not user:
            raise NotFound(
                "User not found"
            )
        
        if not verify_password(data.password, user.hashed_password):
            raise Unauthorized("Wrong password")
        
        access_token = create_access_token(payload={"sub": str(user.id), "role": user.role_name.value})
        refresh_token = generate_refresh_token()
        
        await self._token_repo.create(
            data={
                "user_id": user.id,
                "token_hash": refresh_token.token_hash,
                "expires_at": refresh_token.expires_at
            }
        )

        return AuthorizationPaylaod(
            access_token=access_token,
            refresh_token=refresh_token
        )
            
    async def logout(self, refresh_token: str) -> None:
        filters = [RefreshToken.token_hash == refresh_token]

        token = await self._token_repo.get_one_by_filters(SearchOptions(
            filters=filters
        ))

        if not token:
            raise NotFound("Session not found")
        
        await self._token_repo.delete(token.id)

        return
    
    """
    Обновляет только access_token
    """
    async def refresh(self, refresh_token: str):
        filters = [RefreshToken.token_hash == refresh_token]

        token = await self._token_repo.get_one_by_filters(SearchOptions(
            filters=filters
        ))

        if not token:
            raise Unauthorized
        
        role = token.user.role_name.value
        
        access_token = create_access_token(payload={"sub": str(token.user_id), "role": role})

        return access_token