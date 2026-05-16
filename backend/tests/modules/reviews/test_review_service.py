import uuid
import pytest
import pytest_asyncio

from sqlalchemy import text

from app.modules.reviews.service import ReviewService
from app.modules.reviews.models import ReviewStatusEnum
from app.modules.reviews.schemas import CreateReviewDTO, CreateCommentDTO
from app.modules.articles.models.enum import ArticleStatus
from app.core.exceptions import NotFound, Forbidden, BadRequest

pytestmark = pytest.mark.asyncio


# ── Helpers ────────────────────────────────────────────────────


async def _make_version_for_review(db_session, creator_id) -> uuid.UUID:
    article_id = uuid.uuid4()
    version_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO articles (id, creator_id)
            VALUES (:id, :creator)
        """),
        {"id": str(article_id), "creator": str(creator_id)},
    )
    await db_session.execute(
        text("""
            INSERT INTO article_versions (id, article_id, version_number, title, abstract, keywords, language, pdf_path, status, updated_by_user_id)
            VALUES (:id, :article_id, 1, :title, NULL, :keywords, :lang, :pdf, :status, :updated_by)
        """),
        {
            "id": str(version_id),
            "article_id": str(article_id),
            "title": "Test Article",
            "keywords": [],
            "lang": "en",
            "pdf": "/uploads/test.pdf",
            "status": ArticleStatus.REVIEW.value,
            "updated_by": str(creator_id),
        },
    )
    await db_session.execute(
        text("UPDATE articles SET current_version_id = :version_id WHERE id = :article_id"),
        {"version_id": str(version_id), "article_id": str(article_id)},
    )
    await db_session.flush()
    return version_id


async def _make_assignment(db_session, version_id, reviewer_id) -> uuid.UUID:
    assignment_id = uuid.uuid4()
    await db_session.execute(
        text("""
            INSERT INTO review_assignments (id, article_version_id, reviewer_id)
            VALUES (:id, :version_id, :reviewer_id)
        """),
        {"id": str(assignment_id), "version_id": str(version_id), "reviewer_id": str(reviewer_id)},
    )
    await db_session.flush()
    return assignment_id


@pytest.fixture
def review_service(db_session):
    return ReviewService(db_session)


# ── ASSIGNMENTS ────────────────────────────────────────────────


@pytest.mark.asyncio(loop_scope="session")
class TestGetMyAssignments:

    async def test_empty(self, review_service, test_reviewer):
        result = await review_service.get_my_assignments(test_reviewer["id"])
        assert result == []

    async def test_success(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        await _make_assignment(db_session, version_id, test_reviewer["id"])

        result = await review_service.get_my_assignments(test_reviewer["id"])
        assert len(result) == 1
        assert result[0].article_version_id == version_id
        assert result[0].reviewer_id == test_reviewer["id"]
        assert result[0].review_status is None  # review not yet submitted

    async def test_with_review(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])
        await db_session.execute(
            text("""
                INSERT INTO reviews (id, review_assignment_id, status, completed_at)
                VALUES (:id, :assignment_id, :status, NOW())
            """),
            {"id": str(uuid.uuid4()), "assignment_id": str(assignment_id), "status": ReviewStatusEnum.APPROVED.value},
        )
        await db_session.flush()

        result = await review_service.get_my_assignments(test_reviewer["id"])
        assert len(result) == 1
        assert result[0].review_status == ReviewStatusEnum.APPROVED
        assert result[0].review_completed_at is not None


@pytest.mark.asyncio(loop_scope="session")
class TestGetAssignmentByVersion:

    async def test_success(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        await _make_assignment(db_session, version_id, test_reviewer["id"])

        result = await review_service.get_assignment_by_version(version_id)
        assert result is not None
        assert result.reviewer_id == test_reviewer["id"]

    async def test_not_found(self, review_service):
        result = await review_service.get_assignment_by_version(uuid.uuid4())
        assert result is None


# ── CREATE REVIEW ──────────────────────────────────────────────


@pytest.mark.asyncio(loop_scope="session")
class TestCreateReview:

    async def test_approved(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.APPROVED)
        result = await review_service.create_review(dto, user_id=test_reviewer["id"])

        assert result.review_assignment_id == assignment_id
        assert result.status == ReviewStatusEnum.APPROVED
        assert result.completed_at is not None

        version = await db_session.execute(
            text("SELECT status, published_at FROM article_versions WHERE id = :id"),
            {"id": str(version_id)},
        )
        row = version.one()
        assert row.status == ArticleStatus.PUBLISHED.value
        assert row.published_at is not None

    async def test_rejected(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.REJECTED)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        row = (await db_session.execute(
            text("SELECT status FROM article_versions WHERE id = :id"),
            {"id": str(version_id)},
        )).scalar_one()
        assert row == ArticleStatus.REJECTED.value

    async def test_requesting_changes(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.REQUESTING_CHANGES)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        row = (await db_session.execute(
            text("SELECT status FROM article_versions WHERE id = :id"),
            {"id": str(version_id)},
        )).scalar_one()
        assert row == ArticleStatus.DRAFT.value

    async def test_not_assigned_reviewer(self, db_session, review_service, test_reviewer, test_user):
        other_reviewer_id = uuid.uuid4()
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.APPROVED)
        with pytest.raises(Forbidden, match="not the assigned reviewer"):
            await review_service.create_review(dto, user_id=other_reviewer_id)

    async def test_already_exists(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.APPROVED)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        with pytest.raises(BadRequest, match="already exists"):
            await review_service.create_review(dto, user_id=test_reviewer["id"])

    async def test_assignment_not_found(self, review_service, test_reviewer):
        dto = CreateReviewDTO(review_assignment_id=uuid.uuid4(), status=ReviewStatusEnum.APPROVED)
        with pytest.raises(NotFound, match="assignment"):
            await review_service.create_review(dto, user_id=test_reviewer["id"])

    async def test_version_not_in_review(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        await db_session.execute(
            text("UPDATE article_versions SET status = :status WHERE id = :id"),
            {"status": ArticleStatus.DRAFT.value, "id": str(version_id)},
        )
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        dto = CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.APPROVED)
        with pytest.raises(BadRequest, match="not in review status"):
            await review_service.create_review(dto, user_id=test_reviewer["id"])


# ── GET REVIEW BY ASSIGNMENT ───────────────────────────────────


@pytest.mark.asyncio(loop_scope="session")
class TestGetReviewByAssignment:

    async def test_success(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        await review_service.create_review(
            CreateReviewDTO(review_assignment_id=assignment_id, status=ReviewStatusEnum.APPROVED),
            user_id=test_reviewer["id"],
        )

        result = await review_service.get_review_by_assignment(assignment_id)
        assert result is not None
        assert result.status == ReviewStatusEnum.APPROVED

    async def test_no_review(self, db_session, review_service, test_reviewer, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        assignment_id = await _make_assignment(db_session, version_id, test_reviewer["id"])

        result = await review_service.get_review_by_assignment(assignment_id)
        assert result is None


# ── COMMENTS ───────────────────────────────────────────────────


@pytest.mark.asyncio(loop_scope="session")
class TestComments:

    async def test_create_success(self, db_session, review_service, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])

        dto = CreateCommentDTO(article_version_id=version_id, content="Nice work!")
        result = await review_service.create_comment(dto, user_id=test_user["id"])

        assert result.article_version_id == version_id
        assert result.user_id == test_user["id"]
        assert result.content == "Nice work!"

    async def test_create_version_not_found(self, review_service, test_user):
        dto = CreateCommentDTO(article_version_id=uuid.uuid4(), content="Ghost")
        with pytest.raises(NotFound, match="version"):
            await review_service.create_comment(dto, user_id=test_user["id"])

    async def test_get_empty(self, db_session, review_service, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])
        result = await review_service.get_comments(version_id)
        assert result == []

    async def test_get_success(self, db_session, review_service, test_user):
        version_id = await _make_version_for_review(db_session, test_user["id"])

        dto = CreateCommentDTO(article_version_id=version_id, content="First!")
        await review_service.create_comment(dto, user_id=test_user["id"])
        dto.content = "Second!"
        await review_service.create_comment(dto, user_id=test_user["id"])

        result = await review_service.get_comments(version_id)
        assert len(result) == 2
        assert result[0].content == "First!"
        assert result[1].content == "Second!"
