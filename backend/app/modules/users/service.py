import uuid

from app.core.base import BaseService
from app.core.responses import PaginationMeta
from app.core.exceptions import NotFound

from app.modules.auth.schemas import AccessTokenPayload

from .repository import UserRepository, User
from .models import RoleName
from .schemas import (
    UserPayload, 
    ProfileEditDTO,
    UserFiltersDTO,
    AuthorProfilePayload,
    ReviewerProfilePayload
)

class UserService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._user_repo = UserRepository(self._session)

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    async def get_user(self, id: uuid.UUID) -> UserPayload:
        user = await (
            self._user_repo.query()
            .where(User.id == id)
            .extended_profile()
            .one_or_none(self._session)
        )

        if not user:
            raise NotFound("User not found")
        
        return self._to_dict(user)

    async def get_users(self, filters: UserFiltersDTO) -> tuple[list[UserPayload], PaginationMeta]:
        qb = (
            self._user_repo.query()
            .extended_profile()
            .filter_by_role(filters.role_name)
            .filter_text(filters.query)
        )

        total = await qb.count(self._session)
        items = await qb.limit(filters.limit).offset(filters.offset).all(self._session)

        payloads = [self._to_dict(u) for u in items]
        meta = PaginationMeta(total=total, limit=filters.limit, offset=filters.offset)

        return payloads, meta

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    async def edit_profile(
        self,
        id: uuid.UUID,
        dto: ProfileEditDTO,
        role: RoleName,
    ) -> UserPayload:
        user_data = dto.model_dump(exclude_unset=True, include={"full_name", "avatar_url"})
        if user_data:
            await self._user_repo.update(id, user_data)

        if role == RoleName.AUTHOR and dto.author is not None:
            profile_data = dto.author.model_dump(exclude_unset=True)
            if profile_data:
                await self._user_repo.upsert_author_profile(id, profile_data)

        elif role == RoleName.REVIEWER and dto.reviewer is not None:
            profile_data = dto.reviewer.model_dump(exclude_unset=True)
            if profile_data:
                await self._user_repo.upsert_reviewer_profile(id, profile_data)

        return await self.get_user(id)

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_dict(user: User) -> UserPayload:
        return UserPayload(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            role_name=user.role_name,

            author_profile=(
                AuthorProfilePayload.model_validate(user.author_profile)
                if user.author_profile
                else None
            ),
            reviewer_profile=(
                ReviewerProfilePayload.model_validate(user.reviewer_profile)
                if user.reviewer_profile
                else None
            ),

            created_at=user.created_at,
            updated_at=user.updated_at
        )