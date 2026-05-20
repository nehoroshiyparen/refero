import uuid

from app.core.base import BaseService
from app.core.responses import PaginationMeta
from app.core.exceptions import NotFound, Forbidden

from app.modules.auth.schemas import AccessTokenPayload

from .repositories import UserRepository, AuthorRepository, ReviewerRepository
from .models import User, UserRole, RoleName
from .schemas import (
    UserPayload, 
    ProfileEditDTO,
    UserFiltersDTO,
    AuthorProfilePayload,
    ReviewerProfilePayload,
    CreateAuthorProfileDTO,
    CreateReviewerProfileDTO,
)


class UserService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._user_repo = UserRepository(self._session)
        self._author_repo = AuthorRepository(self._session)
        self._reviewer_repo = ReviewerRepository(self._session)

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
        user_roles: list[RoleName],
    ) -> UserPayload:
        user_data = dto.model_dump(exclude_unset=True, include={"full_name", "avatar_url"})
        if user_data:
            await self._user_repo.update(id, user_data)

        if dto.author is not None:
            if RoleName.AUTHOR not in user_roles:
                raise Forbidden("You need the AUTHOR role to edit author profile")
            profile_data = dto.author.model_dump(exclude_unset=True)
            if profile_data:
                await self._author_repo.upsert(id, profile_data)

        if dto.reviewer is not None:
            if RoleName.REVIEWER not in user_roles:
                raise Forbidden("You need the REVIEWER role to edit reviewer profile")
            profile_data = dto.reviewer.model_dump(exclude_unset=True)
            if profile_data:
                await self._reviewer_repo.upsert(id, profile_data)

        return await self.get_user(id)

    async def _ensure_role(self, user_id: uuid.UUID, role: str) -> None:
        existing = await self._session.get(UserRole, (user_id, role))
        if not existing:
            self._session.add(UserRole(user_id=user_id, role_name=role))
            await self._session.flush()

    async def create_author_profile(
        self,
        user_id: uuid.UUID,
        dto: CreateAuthorProfileDTO,
    ) -> AuthorProfilePayload:
        data = dto.model_dump(exclude_unset=True)
        await self._author_repo.upsert(user_id, data)
        await self._ensure_role(user_id, "AUTHOR")
        profile = await self._author_repo.get_by_user_id(user_id)
        return AuthorProfilePayload.model_validate(profile)

    async def create_reviewer_profile(
        self,
        user_id: uuid.UUID,
        dto: CreateReviewerProfileDTO,
    ) -> ReviewerProfilePayload:
        data = dto.model_dump(exclude_unset=True)
        await self._reviewer_repo.upsert(user_id, data)
        await self._ensure_role(user_id, "REVIEWER")
        profile = await self._reviewer_repo.get_by_user_id(user_id)
        return ReviewerProfilePayload.model_validate(profile)

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
            roles=[ur.role_name for ur in (user.user_roles or [])],

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