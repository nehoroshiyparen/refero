import uuid
from datetime import datetime, timezone

from app.core.base import BaseService
from app.core.exceptions import NotFound, Forbidden, BadRequest
from app.core.responses import PaginationMeta

from app.modules.articles.models.article import Article
from app.modules.articles.models.enum import ArticleStatus
from app.modules.articles.repositories.article_repo import ArticleRepository

from .repository import ReviewRepository
from .models import Review, ReviewStatusEnum
from .schemas import CreateReviewDTO, UpdateReviewDTO, ReviewFiltersDTO, ReviewPayload


_STATUS_MAP = {
    ReviewStatusEnum.PENDING: ArticleStatus.REVIEW,
    ReviewStatusEnum.APPROVED: ArticleStatus.PUBLISHED,
    ReviewStatusEnum.REJECTED: ArticleStatus.REJECTED,
    ReviewStatusEnum.REQUESTING_CHANGES: ArticleStatus.DRAFT,
}


class ReviewService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._review_repo = ReviewRepository(self._session)
        self._article_repo = ArticleRepository(self._session)

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    async def get_my_reviews(
        self,
        user_id: uuid.UUID,
        filters: ReviewFiltersDTO,
    ) -> tuple[list[ReviewPayload], PaginationMeta]:
        qb = self._review_repo.query().filter_by_reviewer(user_id)
        if filters:
            qb.filter_by_status(filters.status).filter_by_article(filters.article_id)
        total = await qb.count(self._session)
        items = await qb.limit(filters.limit).offset(filters.offset).all(self._session)

        payloads = [self._to_payload(r) for r in items]
        meta = PaginationMeta(total=total, limit=filters.limit, offset=filters.offset)

        return payloads, meta

    async def get_article_reviews(self, article_id: uuid.UUID) -> list[ReviewPayload]:
        items = await (
            self._review_repo.query()
            .filter_by_article(article_id)
            .all(self._session)
        )
        return [self._to_payload(r) for r in items]

    # ------------------------------------------------------------------ #
    #  CREATE / UPDATE / REVOKE
    # ------------------------------------------------------------------ #

    async def create_review(
        self,
        dto: CreateReviewDTO,
        user_id: uuid.UUID,
    ) -> ReviewPayload:
        article = await self._get_article_or_fail(dto.article_id)

        if article.status != ArticleStatus.REVIEW.value:
            raise BadRequest("Article must be in review status")

        existing = await (
            self._review_repo.query()
            .filter_by_article(dto.article_id)
            .filter_by_reviewer(user_id)
            .one_or_none(self._session)
        )
        if existing:
            raise BadRequest("You already have a review assigned to this article")

        review = await self._review_repo.create({
            "id": str(uuid.uuid4()),
            "article_id": str(dto.article_id),
            "reviewer_id": str(user_id),
            "status": dto.status.value,
            "comment": dto.comment,
        })

        article_status = _STATUS_MAP[dto.status]
        now = datetime.now(timezone.utc)
        article_data: dict = {"status": article_status.value}
        if article_status == ArticleStatus.PUBLISHED:
            article_data["published_at"] = now

        await self._article_repo.update(dto.article_id, article_data)

        return self._to_payload(review)

    async def update_review(
        self,
        id: uuid.UUID,
        dto: UpdateReviewDTO,
        user_id: uuid.UUID,
    ) -> ReviewPayload:
        review = await self._get_review_or_fail(id)
        await self._check_is_reviewer(review, user_id)

        data = dto.model_dump(exclude_unset=True)
        updated = await self._review_repo.update(id, data)
        return self._to_payload(updated)

    async def revoke_review(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ReviewPayload:
        review = await self._get_review_or_fail(id)
        await self._check_is_reviewer(review, user_id)

        updated = await self._review_repo.update(id, {
            "status": ReviewStatusEnum.REJECTED.value,
        })

        await self._article_repo.update(review.article_id, {
            "status": ArticleStatus.REJECTED.value,
        })

        return self._to_payload(updated)

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_payload(review: Review) -> ReviewPayload:
        return ReviewPayload(
            id=review.id,
            article_id=review.article_id,
            reviewer_id=review.reviewer_id,
            status=ReviewStatusEnum(review.status),
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at,
            completed_at=review.completed_at,
        )

    async def _get_review_or_fail(self, id: uuid.UUID) -> Review:
        review = await (
            self._review_repo.query()
            .where(Review.id == id)
            .one_or_none(self._session)
        )
        if not review:
            raise NotFound("Review not found")
        return review

    async def _get_article_or_fail(self, id: uuid.UUID):
        article = await (
            self._article_repo.query()
            .where(Article.id == id)
            .one_or_none(self._session)
        )
        if not article:
            raise NotFound("Article not found")
        return article

    async def _check_is_reviewer(self, review: Review, user_id: uuid.UUID) -> None:
        if review.reviewer_id != user_id:
            raise Forbidden("You are not the reviewer assigned to this review")
