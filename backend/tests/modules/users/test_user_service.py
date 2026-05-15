import uuid
import pytest
import pytest_asyncio

from sqlalchemy import text

from app.modules.users.service import UserService
from app.modules.users.models import RoleName
from app.modules.users.schemas import UserFiltersDTO, ProfileEditDTO, AuthorProfileFields, ReviewerProfileFields
from app.core.exceptions import NotFound

pytestmark = pytest.mark.asyncio


@pytest.fixture
def user_service(db_session):
    return UserService(db_session)


@pytest.mark.asyncio(loop_scope="session")
class TestGetUser:

    async def test_get_user_success(self, user_service, test_user):
        result = await user_service.get_user(test_user["id"])

        assert result.id == test_user["id"]
        assert result.full_name == test_user["full_name"]
        assert result.username == test_user["username"]
        assert result.email == test_user["email"]
        assert result.role_name == RoleName.AUTHOR

    async def test_get_user_with_profiles(self, user_service, test_user, db_session):
        await db_session.execute(
            text("""
                INSERT INTO author_profiles (user_id, organization, position)
                VALUES (:uid, :org, :pos)
                ON CONFLICT (user_id) DO UPDATE SET organization = :org2, position = :pos2
            """),
            {"uid": str(test_user["id"]), "org": "MIT", "pos": "Researcher",
             "org2": "MIT", "pos2": "Researcher"},
        )
        await db_session.flush()

        result = await user_service.get_user(test_user["id"])

        assert result.author_profile is not None
        assert result.author_profile.organization == "MIT"
        assert result.author_profile.position == "Researcher"

    async def test_get_user_not_found(self, user_service):
        with pytest.raises(NotFound):
            await user_service.get_user(uuid.uuid4())


@pytest.mark.asyncio(loop_scope="session")
class TestGetUsers:

    async def test_get_users_all(self, user_service, test_user):
        items, meta = await user_service.get_users(UserFiltersDTO())

        assert isinstance(items, list)
        assert meta.total >= 1

    async def test_get_users_filter_by_role(self, user_service, test_user):
        items, meta = await user_service.get_users(
            UserFiltersDTO(role_name=RoleName.AUTHOR)
        )

        assert len(items) >= 1
        assert all(u.role_name == RoleName.AUTHOR for u in items)

    async def test_get_users_filter_by_role_no_match(self, user_service):
        items, meta = await user_service.get_users(
            UserFiltersDTO(role_name=RoleName.ADMIN)
        )

        assert len(items) == 0
        assert meta.total == 0

    async def test_get_users_filter_text(self, user_service, test_user):
        items, meta = await user_service.get_users(
            UserFiltersDTO(query=test_user["username"])
        )

        assert len(items) >= 1

    async def test_get_users_filter_text_no_match(self, user_service):
        items, meta = await user_service.get_users(
            UserFiltersDTO(query="nonexistent_user_xyz")
        )

        assert len(items) == 0

    async def test_get_users_pagination(self, user_service, test_user):
        items, meta = await user_service.get_users(
            UserFiltersDTO(limit=1, offset=0)
        )

        assert len(items) <= 1
        assert meta.limit == 1
        assert meta.offset == 0


@pytest.mark.asyncio(loop_scope="session")
class TestEditProfile:

    async def test_edit_user_fields(self, user_service, test_user):
        dto = ProfileEditDTO(full_name="Updated Name")
        result = await user_service.edit_profile(
            test_user["id"], dto, role=RoleName.AUTHOR
        )

        assert result.full_name == "Updated Name"

    async def test_edit_author_profile(self, user_service, test_user):
        dto = ProfileEditDTO(
            author=AuthorProfileFields(
                organization="Stanford",
                degree="PhD",
                bio="A great researcher",
            )
        )
        result = await user_service.edit_profile(
            test_user["id"], dto, role=RoleName.AUTHOR
        )

        assert result.author_profile is not None
        assert result.author_profile.organization == "Stanford"
        assert result.author_profile.degree == "PhD"
        assert result.author_profile.bio == "A great researcher"

    async def test_edit_author_profile_partial(self, user_service, test_user):
        dto = ProfileEditDTO(
            author=AuthorProfileFields(position="Professor")
        )
        result = await user_service.edit_profile(
            test_user["id"], dto, role=RoleName.AUTHOR
        )

        assert result.author_profile is not None
        assert result.author_profile.position == "Professor"

    async def test_edit_author_profile_upsert(self, user_service, test_user, db_session):
        other_id = uuid.uuid4()
        await db_session.execute(
            text("""
                INSERT INTO users (id, username, email, hashed_password, full_name, role_name, is_active)
                VALUES (:id, :uname, :email, :pw, :name, :role, :is_active)
            """),
            {
                "id": str(other_id),
                "uname": f"new_user_{other_id.hex[:8]}",
                "email": f"new_{other_id.hex[:8]}@test.com",
                "pw": "fake_hash",
                "name": "New User",
                "role": "AUTHOR",
                "is_active": True
            },
        )
        await db_session.flush()

        dto = ProfileEditDTO(
            author=AuthorProfileFields(organization="Harvard")
        )
        result = await user_service.edit_profile(
            other_id, dto, role=RoleName.AUTHOR
        )

        assert result.author_profile is not None
        assert result.author_profile.organization == "Harvard"

    async def test_edit_reviewer_profile(self, user_service, db_session):
        reviewer_id = uuid.uuid4()
        await db_session.execute(
            text("""
                INSERT INTO users (id, username, email, hashed_password, full_name, role_name, is_active)
                VALUES (:id, :uname, :email, :pw, :name, :role, :is_active)
            """),
            {
                "id": str(reviewer_id),
                "uname": f"reviewer_{reviewer_id.hex[:8]}",
                "email": f"rev_{reviewer_id.hex[:8]}@test.com",
                "pw": "fake_hash",
                "name": "Test Reviewer",
                "role": "REVIEWER",
                "is_active": True
            },
        )
        await db_session.flush()

        dto = ProfileEditDTO(
            reviewer=ReviewerProfileFields(
                specialization="Computer Science",
                degree="MSc",
            )
        )
        result = await user_service.edit_profile(
            reviewer_id, dto, role=RoleName.REVIEWER
        )

        assert result.reviewer_profile is not None
        assert result.reviewer_profile.specialization == "Computer Science"
        assert result.reviewer_profile.degree == "MSc"

    async def test_edit_profile_not_found(self, user_service):
        dto = ProfileEditDTO(full_name="Ghost")

        with pytest.raises(NotFound):
            await user_service.edit_profile(
                uuid.uuid4(), dto, role=RoleName.AUTHOR
            )
