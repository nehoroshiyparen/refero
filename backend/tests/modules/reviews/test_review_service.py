import uuid
import pytest
import pytest_asyncio

from sqlalchemy import text

from app.modules.reviews.service import ReviewService
from app.modules.reviews.models import ReviewStatusEnum
from app.modules.reviews.schemas import CreateReviewDTO, UpdateReviewDTO, ReviewFiltersDTO
from app.modules.articles.models.enum import ArticleStatus
from app.core.exceptions import NotFound, Forbidden, BadRequest

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(loop_scope="session")
async def test_reviewer(db_session) -> dict:
    from app.modules.users.models.user import User

    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        username=f"test_reviewer_{user_id.hex[:8]}",
        email=f"reviewer_{user_id.hex[:8]}@test.com",
        hashed_password="fake_hash",
        full_name="Test Reviewer",
        role_name="REVIEWER",
    )
    db_session.add(user)
    await db_session.flush()
    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
    }


@pytest.fixture
def review_service(db_session):
    return ReviewService(db_session)


def _make_review_article(db_session, creator_id) -> uuid.UUID:
    article_id = uuid.uuid4()
    db_session.execute(
        text("""
            INSERT INTO articles (id, title, pdf_path, creator_id, status)
            VALUES (:id, :title, :pdf, :creator, :status)
        """),
        {
            "id": str(article_id),
            "title": "Review Target Article",
            "pdf": "/uploads/review.pdf",
            "creator": str(creator_id),
            "status": ArticleStatus.REVIEW.value,
        },
    )
    db_session.flush()
    return article_id


# ── GET MY REVIEWS ────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestGetMyReviews:

    async def test_my_reviews_with_filter(
        self, db_session, review_service, test_reviewer, test_user
    ):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        items = await review_service.get_my_reviews(
            user_id=test_reviewer["id"],
            filters=ReviewFiltersDTO(status=ReviewStatusEnum.PENDING),
        )
        assert len(items) == 1
        assert items[0].status == ReviewStatusEnum.PENDING

    async def test_my_reviews_empty(
        self, review_service, test_user
    ):
        items = await review_service.get_my_reviews(user_id=test_user["id"])
        assert items == []


# ── GET ARTICLE REVIEWS ───────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestGetArticleReviews:

    async def test_article_reviews_success(
        self, db_session, review_service, test_reviewer, test_user
    ):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        items = await review_service.get_article_reviews(article_id)
        assert len(items) == 1
        assert items[0].article_id == article_id

    async def test_article_reviews_empty(self, review_service):
        items = await review_service.get_article_reviews(uuid.uuid4())
        assert items == []


# ── CREATE REVIEW ─────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestCreateReview:

    async def test_pending(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(
            article_id=article_id,
            status=ReviewStatusEnum.PENDING,
            comment="Will review soon",
        )
        result = await review_service.create_review(dto, user_id=test_reviewer["id"])

        assert result.article_id == article_id
        assert result.reviewer_id == test_reviewer["id"]
        assert result.status == ReviewStatusEnum.PENDING
        assert result.comment == "Will review soon"

        article = await review_service._get_article_or_fail(article_id)
        assert article.status == ArticleStatus.REVIEW.value

    async def test_approved(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(
            article_id=article_id,
            status=ReviewStatusEnum.APPROVED,
            comment="Looks great!",
        )
        result = await review_service.create_review(dto, user_id=test_reviewer["id"])

        assert result.status == ReviewStatusEnum.APPROVED

        article = await review_service._get_article_or_fail(article_id)
        assert article.status == ArticleStatus.PUBLISHED.value
        assert article.published_at is not None

    async def test_rejected(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(
            article_id=article_id,
            status=ReviewStatusEnum.REJECTED,
        )
        result = await review_service.create_review(dto, user_id=test_reviewer["id"])

        assert result.status == ReviewStatusEnum.REJECTED

        article = await review_service._get_article_or_fail(article_id)
        assert article.status == ArticleStatus.REJECTED.value

    async def test_requesting_changes(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(
            article_id=article_id,
            status=ReviewStatusEnum.REQUESTING_CHANGES,
        )
        result = await review_service.create_review(dto, user_id=test_reviewer["id"])

        assert result.status == ReviewStatusEnum.REQUESTING_CHANGES

        article = await review_service._get_article_or_fail(article_id)
        assert article.status == ArticleStatus.DRAFT.value

    async def test_article_not_in_review(self, db_session, review_service, test_reviewer, test_user):
        article_id = uuid.uuid4()
        db_session.execute(
            text("""
                INSERT INTO articles (id, title, pdf_path, creator_id, status)
                VALUES (:id, :title, :pdf, :creator, :status)
            """),
            {
                "id": str(article_id),
                "title": "Draft Article",
                "pdf": "/uploads/draft.pdf",
                "creator": str(test_user["id"]),
                "status": ArticleStatus.DRAFT.value,
            },
        )
        db_session.flush()

        dto = CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING)
        with pytest.raises(BadRequest, match="review status"):
            await review_service.create_review(dto, user_id=test_reviewer["id"])

    async def test_duplicate(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        dto = CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING)
        await review_service.create_review(dto, user_id=test_reviewer["id"])

        with pytest.raises(BadRequest, match="already"):
            await review_service.create_review(dto, user_id=test_reviewer["id"])

    async def test_article_not_found(self, review_service, test_reviewer):
        dto = CreateReviewDTO(article_id=uuid.uuid4(), status=ReviewStatusEnum.PENDING)
        with pytest.raises(NotFound):
            await review_service.create_review(dto, user_id=test_reviewer["id"])


# ── UPDATE REVIEW ─────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestUpdateReview:

    async def test_comment(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        created = await review_service.create_review(
            CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING),
            user_id=test_reviewer["id"],
        )

        dto = UpdateReviewDTO(comment="Updated comment")
        result = await review_service.update_review(
            created.id, dto, user_id=test_reviewer["id"]
        )
        assert result.comment == "Updated comment"

    async def test_not_reviewer(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        created = await review_service.create_review(
            CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING),
            user_id=test_reviewer["id"],
        )

        dto = UpdateReviewDTO(comment="Hacked")
        with pytest.raises(Forbidden):
            await review_service.update_review(
                created.id, dto, user_id=test_user["id"]
            )

    async def test_not_found(self, review_service, test_reviewer):
        dto = UpdateReviewDTO(comment="Ghost")
        with pytest.raises(NotFound):
            await review_service.update_review(
                uuid.uuid4(), dto, user_id=test_reviewer["id"]
            )


# ── REVOKE REVIEW ─────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestRevokeReview:

    async def test_revoke_approved(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        created = await review_service.create_review(
            CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.APPROVED),
            user_id=test_reviewer["id"],
        )

        result = await review_service.revoke_review(
            created.id, user_id=test_reviewer["id"]
        )
        assert result.status == ReviewStatusEnum.REJECTED

        article = await review_service._get_article_or_fail(article_id)
        assert article.status == ArticleStatus.REJECTED.value

    async def test_not_reviewer(self, db_session, review_service, test_reviewer, test_user):
        article_id = _make_review_article(db_session, test_user["id"])
        created = await review_service.create_review(
            CreateReviewDTO(article_id=article_id, status=ReviewStatusEnum.PENDING),
            user_id=test_reviewer["id"],
        )

        with pytest.raises(Forbidden):
            await review_service.revoke_review(
                created.id, user_id=test_user["id"]
            )

    async def test_not_found(self, review_service, test_reviewer):
        with pytest.raises(NotFound):
            await review_service.revoke_review(
                uuid.uuid4(), user_id=test_reviewer["id"]
            )
