import uuid
from datetime import datetime, timezone

from sqlalchemy import func

from app.core.base import BaseService
from app.core.exceptions import NotFound, Forbidden, BadRequest
from app.core.responses import PaginationMeta

from app.modules.articles.models.article_version import ArticleVersion
from app.modules.articles.models.enum import ArticleStatus
from app.modules.articles.repositories import ArticleVersionRepository

from .repository import ReviewRepository
from .repositories import ReviewAssignmentRepository, VersionCommentRepository
from .models import Review, ReviewAssignment, ReviewStatusEnum, VersionComment
from .schemas import CreateReviewDTO, CreateCommentDTO, ReviewPayload, ReviewAssignmentPayload, ReviewAssignmentFullPayload, CommentPayload


_STATUS_MAP = {
    ReviewStatusEnum.APPROVED: ArticleStatus.PUBLISHED,
    ReviewStatusEnum.REJECTED: ArticleStatus.REJECTED,
    ReviewStatusEnum.REQUESTING_CHANGES: ArticleStatus.DRAFT,
}


class ReviewService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._review_repo = ReviewRepository(self._session)
        self._assignment_repo = ReviewAssignmentRepository(self._session)
        self._comment_repo = VersionCommentRepository(self._session)
        self._version_repo = ArticleVersionRepository(self._session)

    # ------------------------------------------------------------------ #
    #  ASSIGNMENTS
    # ------------------------------------------------------------------ #

    async def get_my_assignments(
        self,
        user_id: uuid.UUID,
    ) -> list[ReviewAssignmentFullPayload]:
        items = await (
            self._assignment_repo.query()
            .filter_by_reviewer(user_id)
            .with_review()
            .with_article_version_and_article()
            .all(self._session)
        )
        return [self._to_assignment_full_payload(a) for a in items]

    async def get_assignment_by_id(
        self,
        assignment_id: uuid.UUID,
    ) -> ReviewAssignmentFullPayload | None:
        item = await (
            self._assignment_repo.query()
            .where(ReviewAssignment.id == assignment_id)
            .with_review()
            .with_article_version_and_article()
            .one_or_none(self._session)
        )
        if not item:
            return None
        return self._to_assignment_full_payload(item)

    async def get_assignment_by_version(
        self,
        article_version_id: uuid.UUID,
    ) -> ReviewAssignmentFullPayload | None:
        item = await (
            self._assignment_repo.query()
            .filter_by_version(article_version_id)
            .with_review()
            .with_article_version_and_article()
            .one_or_none(self._session)
        )
        if not item:
            return None
        return self._to_assignment_full_payload(item)

    # ------------------------------------------------------------------ #
    #  REVIEWS
    # ------------------------------------------------------------------ #

    async def create_review(
        self,
        dto: CreateReviewDTO,
        user_id: uuid.UUID,
    ) -> ReviewPayload:
        assignment = await self._get_assignment_or_fail(dto.review_assignment_id)

        if assignment.reviewer_id != user_id:
            raise Forbidden("You are not the assigned reviewer for this version")

        if assignment.review is not None:
            raise BadRequest("A review already exists for this assignment")

        version = assignment.article_version
        if version.status != ArticleStatus.REVIEW.value:
            raise BadRequest("Article version is not in review status")

        review = await self._review_repo.create({
            "id": uuid.uuid4(),
            "review_assignment_id": dto.review_assignment_id,
            "status": dto.status.value,
        })

        version_status = _STATUS_MAP[dto.status]
        version_data: dict = {"status": version_status.value}
        if version_status == ArticleStatus.PUBLISHED:
            version_data["published_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

        await self._version_repo.update(assignment.article_version_id, version_data)

        review_data = {"completed_at": datetime.now(timezone.utc).replace(tzinfo=None)}
        await self._review_repo.update(review.id, review_data)

        full_review = await (
            self._review_repo.query()
            .where(Review.id == review.id)
            .one_or_none(self._session)
        )
        return self._to_payload(full_review)

    async def get_review_by_assignment(
        self,
        assignment_id: uuid.UUID,
    ) -> ReviewPayload | None:
        review = await (
            self._review_repo.query()
            .filter_by_assignment(assignment_id)
            .one_or_none(self._session)
        )
        if not review:
            return None
        return self._to_payload(review)

    # ------------------------------------------------------------------ #
    #  COMMENTS
    # ------------------------------------------------------------------ #

    async def create_comment(
        self,
        dto: CreateCommentDTO,
        user_id: uuid.UUID,
    ) -> CommentPayload:
        version = await (
            self._version_repo.query()
            .where(ArticleVersion.id == dto.article_version_id)
            .one_or_none(self._session)
        )
        if not version:
            raise NotFound("Article version not found")

        comment = await self._comment_repo.create({
            "id": uuid.uuid4(),
            "article_version_id": dto.article_version_id,
            "user_id": user_id,
            "content": dto.content,
        })

        loaded = await (
            self._comment_repo.query()
            .where(VersionComment.id == comment.id)
            .with_user()
            .one_or_none(self._session)
        )
        return self._to_comment_payload(loaded or comment)

    async def get_comments(
        self,
        article_version_id: uuid.UUID,
    ) -> list[CommentPayload]:
        items = await (
            self._comment_repo.query()
            .where(VersionComment.article_version_id == article_version_id)
            .with_user()
            .order_by(VersionComment.created_at.asc())
            .all(self._session)
        )
        return [self._to_comment_payload(c) for c in items]

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #

    async def _get_assignment_or_fail(self, id: uuid.UUID) -> ReviewAssignment:
        item = await (
            self._assignment_repo.query()
            .where(ReviewAssignment.id == id)
            .with_review()
            .with_article_version()
            .one_or_none(self._session)
        )
        if not item:
            raise NotFound("Review assignment not found")
        return item

    @staticmethod
    def _to_payload(review: Review) -> ReviewPayload:
        return ReviewPayload(
            id=review.id,
            review_assignment_id=review.review_assignment_id,
            status=ReviewStatusEnum(review.status),
            created_at=review.created_at,
            completed_at=review.completed_at,
        )

    @staticmethod
    def _to_assignment_full_payload(a: ReviewAssignment) -> ReviewAssignmentFullPayload:
        av = a.article_version
        return ReviewAssignmentFullPayload(
            id=a.id,
            article_version_id=a.article_version_id,
            reviewer_id=a.reviewer_id,
            created_at=a.created_at,
            review_status=ReviewStatusEnum(a.review.status) if a.review else None,
            review_completed_at=a.review.completed_at if a.review else None,
            article_id=av.article_id if av else None,
            article_title=av.title if av else None,
            version_number=av.version_number if av else None,
            version_title=av.title if av else None,
        )

    @staticmethod
    def _to_comment_payload(c) -> CommentPayload:
        return CommentPayload(
            id=c.id,
            article_version_id=c.article_version_id,
            user_id=c.user_id,
            user_name=c.user.full_name if hasattr(c, 'user') and c.user else "",
            content=c.content,
            created_at=c.created_at,
        )
