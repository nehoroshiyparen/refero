import uuid
from datetime import datetime, timezone

from sqlalchemy import func

from app.core.base import BaseService
from app.core.exceptions import NotFound, Forbidden, BadRequest
from app.core.responses import PaginationMeta

from app.modules.journals.repository import JournalRepository, Journal
from app.modules.citations.service import CitationService
from app.modules.citations.schemas import CitationBriefPayload
from app.modules.citations.models import CitationMatchStatus

from .repositories import (
    ArticleRepository,
    ArticleAuthorsRepository,
    ArticleApprovalsRepository,
    ArticleVersionRepository,
)
from .models import (
    Article,
    ArticleVersion,
    ArticleAuthors,
    ApprovalStatus,
    ArticleApprovals,
    ArticleStatus
)
from app.modules.reviews.repositories import ReviewAssignmentRepository
from app.modules.reviews.models.review_assignment import ReviewAssignment
from .schemas import (
    ArticleCreateDTO,
    ArticleUpdateDTO,
    ArticleFiltersDTO,
    AddAuthorDTO,
    ArticlePayload,
    ArticleFullPayload,
    ArticleVersionPayload,
    AuthorBriefPayload,
    JournalBriefPayload,
    ApprovalSubmissionPayload,
    AuthorActionPayload,
)


class ArticleService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._article_repo = ArticleRepository(self._session)
        self._version_repo = ArticleVersionRepository(self._session)
        self._article_approvals_repo = ArticleApprovalsRepository(self._session)
        self._article_authors_repo = ArticleAuthorsRepository(self._session)
        self._journal_repo: JournalRepository = JournalRepository(self._session)
        self._assignment_repo = ReviewAssignmentRepository(self._session)

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    async def get_articles(self, filters: ArticleFiltersDTO) -> tuple[list[ArticlePayload], PaginationMeta]:
        qb = (
            self._article_repo.query()
            .filter_status(filters.status)
            .filter_journal(filters.journal_id)
            .filter_language(filters.language)
            .filter_author(filters.author_id)
            .filter_keywords(filters.keywords)
            .filter_text(filters.query)
            .with_current_version()
        )

        total = await qb.count(self._session)
        items = await qb.limit(filters.limit).offset(filters.offset).all(self._session)

        payloads = [self._to_payload(a) for a in items]
        meta = PaginationMeta(total=total, limit=filters.limit, offset=filters.offset)

        return payloads, meta

    async def get_article_by_id(
        self,
        id: uuid.UUID,
        anonymous: bool = False,
    ) -> ArticleFullPayload:
        article = await self._get_article_full_or_fail(id)
        article.view_count += 1
        await self._article_repo.update(id, {"view_count": article.view_count})
        payload = self._to_full_payload(article)
        if anonymous:
            for author in payload.authors:
                author.name = ""
                author.email = ""
        return payload

    async def get_article_versions(
        self,
        article_id: uuid.UUID,
        status: ArticleStatus | None = None,
        approved_only: bool = False,
    ) -> list[ArticleVersionPayload]:
        article = await self._get_article_or_fail(article_id)

        qb = (
            self._version_repo.query()
            .where(ArticleVersion.article_id == article_id)
            .filter_status(status)
            .filter_approved_only(approved_only)
        )

        versions = await qb.all(self._session)
        return [self._to_version_payload(v) for v in versions]

    # ------------------------------------------------------------------ #
    #  CREATE / UPDATE / DELETE
    # ------------------------------------------------------------------ #

    async def create_article(
        self,
        dto: ArticleCreateDTO,
        user_id: uuid.UUID,
    ) -> ArticleFullPayload:
        if dto.journal_id:
            journal_exists = await (
                self._journal_repo.query()
                .where(Journal.id == dto.journal_id)
                .one_or_none(self._session)
            )

            if not journal_exists:
                raise NotFound("Specified journal is not found")

        article_id = uuid.uuid4()

        article = await self._article_repo.create({
            "id": article_id,
            "creator_id": user_id,
            "journal_id": dto.journal_id,
            "is_visible": True,
        })

        version_id = uuid.uuid4()
        await self._version_repo.create({
            "id": version_id,
            "article_id": article_id,
            "version_number": 1,
            "title": dto.title,
            "abstract": dto.abstract,
            "keywords": dto.keywords,
            "language": dto.language,
            "pdf_path": dto.pdf_path,
            "status": ArticleStatus.DRAFT.value,
            "updated_by_user_id": user_id,
        })

        article.current_version_id = version_id
        await self._session.flush()

        await self._article_authors_repo.create({
            "id": uuid.uuid4(),
            "article_id": article_id,
            "author_id": user_id,
        })

        if dto.citations:
            citation_service = CitationService(self._session)
            await citation_service.resolve_citations(
                article.id,
                citations=dto.citations
            )

        await self._session.flush()

        full = await self._get_article_full_or_fail(article.id)
        return self._to_full_payload(full)

    async def update_article(
        self,
        id: uuid.UUID,
        dto: ArticleUpdateDTO,
        user_id: uuid.UUID,
    ) -> ArticleFullPayload:
        article = await self._get_article_or_fail(id)

        if not article.current_version:
            raise NotFound("Article has no current version")

        if article.current_version.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only update articles in draft status")

        await self._check_is_author(id, user_id)

        version_data: dict = dto.model_dump(exclude_unset=True)
        journal_id_val = version_data.pop("journal_id", None)

        if version_data:
            version_data["updated_by_user_id"] = user_id
            await self._version_repo.update(
                article.current_version.id,
                version_data,
            )

        if journal_id_val is not None:
            journal = await (
                self._journal_repo.query()
                .where(Journal.id == journal_id_val)
                .one_or_none(self._session)
            )
            if not journal:
                raise NotFound("Specified journal is not found")
            await self._article_repo.update(id, {"journal_id": journal_id_val})
        elif "journal_id" in dto.model_dump(exclude_unset=True):
            await self._article_repo.update(id, {"journal_id": None})

        if dto.citations is not None:
            citation_service = CitationService(self._session)
            await citation_service.replace_citations(
                id,
                citations=dto.citations,
            )

        full = await self._get_article_full_or_fail(id)
        return self._to_full_payload(full)

    async def create_article_version(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ArticleVersionPayload:
        article = await self._get_article_or_fail(id)

        if not article.current_version:
            raise NotFound("Article has no current version")

        await self._check_is_author(id, user_id)

        current = article.current_version
        max_version = await (
            self._version_repo.query()
            .where(ArticleVersion.article_id == id)
            .order_by(ArticleVersion.version_number.desc())
            .one_or_none(self._session)
        )
        next_version_number = (max_version.version_number + 1) if max_version else 1

        version = await self._version_repo.create({
            "id": uuid.uuid4(),
            "article_id": id,
            "version_number": next_version_number,
            "title": current.title,
            "abstract": current.abstract,
            "keywords": current.keywords,
            "language": current.language,
            "pdf_path": current.pdf_path,
            "status": ArticleStatus.DRAFT.value,
            "updated_by_user_id": user_id,
        })

        article.current_version_id = version.id
        await self._session.flush()

        return self._to_version_payload(version)

    async def set_current_version(
        self,
        article_id: uuid.UUID,
        version_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ArticleFullPayload:
        article = await self._get_article_full_or_fail(article_id)

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can change the current version")

        version = await (
            self._version_repo.query()
            .where(ArticleVersion.id == version_id, ArticleVersion.article_id == article_id)
            .one_or_none(self._session)
        )
        if not version:
            raise NotFound("Version not found")

        article.current_version_id = version_id
        await self._session.flush()

        full = await self._get_article_full_or_fail(article_id)
        return self._to_full_payload(full)

    async def delete_version(
        self,
        article_id: uuid.UUID,
        version_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        article = await self._get_article_or_fail(article_id)

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can delete versions")

        if article.current_version_id == version_id:
            raise BadRequest("Cannot delete the current version")

        version = await (
            self._version_repo.query()
            .where(ArticleVersion.id == version_id)
            .one_or_none(self._session)
        )
        if not version:
            raise NotFound("Version not found")

        await self._version_repo.delete(version_id)

    async def delete_article(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        article = await self._get_article_or_fail(id)

        if article.current_version and article.current_version.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only delete articles in draft status")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can delete it")

        await self._article_repo.delete(id)

    # ------------------------------------------------------------------ #
    #  VISIBILITY
    # ------------------------------------------------------------------ #

    async def hide_article(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ArticlePayload:
        article = await self._get_article_or_fail(id)

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can hide it")

        updated = await self._article_repo.update(id, {"is_visible": False})
        return self._to_payload(updated)

    async def show_article(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ArticlePayload:
        article = await self._get_article_or_fail(id)

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can show it")

        updated = await self._article_repo.update(id, {"is_visible": True})
        return self._to_payload(updated)

    # ------------------------------------------------------------------ #
    #  APPROVAL WORKFLOW
    # ------------------------------------------------------------------ #

    async def submit_for_approval(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ApprovalSubmissionPayload:
        article = await self._get_article_or_fail(id)

        version = await (
            self._version_repo.query()
            .where(ArticleVersion.article_id == id)
            .order_by(ArticleVersion.version_number.desc())
            .one_or_none(self._session)
        )
        if not version:
            raise NotFound("No versions found for this article")

        if version.status != ArticleStatus.DRAFT.value:
            raise BadRequest("Can only submit draft articles for approval")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can submit for approval")

        co_authors = await (
            self._article_authors_repo.query()
            .where(
                ArticleAuthors.article_id == id,
                ArticleAuthors.author_id != user_id,
            )
            .all(self._session)
        )

        if not co_authors:
            await self._assign_random_reviewer(version.id)
            await self._version_repo.update(version.id, {
                "status": ArticleStatus.REVIEW.value,
            })
            return ApprovalSubmissionPayload(
                message="Article submitted for review (no co-authors to approve)"
            )

        for co_author in co_authors:
            await self._article_approvals_repo.create({
                "id": uuid.uuid4(),
                "article_version_id": version.id,
                "approver_id": co_author.author_id,
                "status": ApprovalStatus.PENDING.value,
            })

        await self._version_repo.update(version.id, {
            "status": ArticleStatus.PENDING_APPROVAL.value,
        })

        return ApprovalSubmissionPayload(
            message=f"Article submitted for approval. Waiting for {len(co_authors)} co-author(s)"
        )

    async def approve_version(
        self,
        article_id: uuid.UUID,
        version_id: uuid.UUID,
        user_id: uuid.UUID,
        approved: bool,
    ) -> ApprovalSubmissionPayload:
        article = await self._get_article_or_fail(article_id)

        version = await (
            self._version_repo.query()
            .where(ArticleVersion.id == version_id)
            .one_or_none(self._session)
        )
        if not version:
            raise NotFound("Version not found")

        if version.status != ArticleStatus.PENDING_APPROVAL.value:
            raise BadRequest("Version is not pending approval")

        approval = await (
            self._article_approvals_repo.query()
            .where(
                ArticleApprovals.article_version_id == version_id,
                ArticleApprovals.approver_id == user_id,
            )
            .one_or_none(self._session)
        )
        if not approval:
            raise Forbidden("You are not an approver for this version")

        if approval.status != ApprovalStatus.PENDING.value:
            raise BadRequest("You have already responded to this approval request")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if not approved:
            await self._article_approvals_repo.update(approval.id, {
                "status": ApprovalStatus.REJECTED.value,
                "approved_at": now,
            })
            await self._version_repo.update(version_id, {
                "status": ArticleStatus.DRAFT.value,
            })
            return ApprovalSubmissionPayload(message="Version rejected, returned to draft")

        await self._article_approvals_repo.update(approval.id, {
            "status": ApprovalStatus.APPROVED.value,
            "approved_at": now,
        })

        remaining_pending = await (
            self._article_approvals_repo.query()
            .where(
                ArticleApprovals.article_version_id == version_id,
                ArticleApprovals.status == ApprovalStatus.PENDING.value,
            )
            .count(self._session)
        )

        if remaining_pending == 0:
            await self._assign_random_reviewer(version_id)
            await self._version_repo.update(version_id, {
                "status": ArticleStatus.REVIEW.value,
            })
            return ApprovalSubmissionPayload(
                message="All co-authors approved. Version sent to review"
            )

        return ApprovalSubmissionPayload(
            message=f"Approved. Waiting for {remaining_pending} more co-author(s)"
        )

    # ------------------------------------------------------------------ #
    #  AUTHORS MANAGEMENT
    # ------------------------------------------------------------------ #

    async def add_author(
        self,
        article_id: uuid.UUID,
        dto: AddAuthorDTO,
        user_id: uuid.UUID,
    ) -> AuthorActionPayload:
        article = await self._get_article_or_fail(article_id)

        if article.current_version and article.current_version.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only add authors to draft articles")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can add co-authors")

        await self._check_not_already_author(article_id, dto.author_id)

        await self._article_authors_repo.create({
            "id": uuid.uuid4(),
            "article_id": article_id,
            "author_id": dto.author_id,
        })

        return AuthorActionPayload(
            message="Author added successfully",
            author_id=dto.author_id,
        )

    async def delete_author(
        self,
        article_id: uuid.UUID,
        author_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> AuthorActionPayload:
        article = await self._get_article_or_fail(article_id)

        if article.current_version and article.current_version.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only remove authors from draft articles")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can remove co-authors")

        if author_id == user_id:
            raise BadRequest("Cannot remove the article creator as an author")

        link = await (
            self._article_authors_repo.query()
            .where(
                ArticleAuthors.article_id == article_id,
                ArticleAuthors.author_id == author_id,
            )
            .one_or_none(self._session)
        )

        if not link:
            raise NotFound("Author not found in this article")

        await self._article_authors_repo.delete(link.id)

        return AuthorActionPayload(
            message="Author removed successfully",
            author_id=author_id,
        )

    # ------------------------------------------------------------------ #
    #  DOWNLOAD
    # ------------------------------------------------------------------ #

    async def download_article(self, id: uuid.UUID) -> str:
        article = await self._get_article_or_fail(id)

        if not article.current_version or not article.current_version.pdf_path:
            raise NotFound("Article has no PDF file")

        await self._article_repo.update(id, {"download_count": article.download_count + 1})

        return article.current_version.pdf_path

    # ------------------------------------------------------------------ #
    #  MAPPER HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_payload(article: Article) -> ArticlePayload:
        cv = article.current_version
        return ArticlePayload(
            id=article.id,
            current_version_id=article.current_version_id,
            title=cv.title if cv else "",
            abstract=cv.abstract if cv else None,
            keywords=cv.keywords or [] if cv else [],
            language=cv.language if cv else "en",
            doi=article.doi,
            pdf_path=cv.pdf_path if cv else "",
            journal_id=article.journal_id,
            status=ArticleStatus(cv.status) if cv else ArticleStatus.DRAFT,
            version_number=cv.version_number if cv else 1,
            is_visible=article.is_visible,
            view_count=article.view_count,
            download_count=article.download_count,
            creator_id=article.creator_id,
            updated_by_user_id=cv.updated_by_user_id if cv else None,
            published_at=cv.published_at if cv else None,
            created_at=article.created_at,
            updated_at=cv.updated_at if cv else None,
        )

    @staticmethod
    def _to_full_payload(article: Article) -> ArticleFullPayload:
        authors = []
        for aa in (article.authors or []):
            authors.append(AuthorBriefPayload(
                author_id=aa.author_id,
                name=aa.author.full_name if aa.author else "",
                email=aa.author.email if aa.author else "",
                joined_at=aa.created_at,
            ))

        journal = None
        if article.journal:
            journal = JournalBriefPayload(
                id=article.journal.id,
                name=article.journal.name,
            )

        citations = []
        for c in (article.citations_from or []):
            citations.append(CitationBriefPayload(
                id=c.id,
                to_article_id=c.to_article_id,
                doi=c.doi,
                raw_reference=c.raw_reference,
                match_status=CitationMatchStatus(c.match_status),
                created_at=c.created_at,
            ))

        cv = article.current_version
        return ArticleFullPayload(
            id=article.id,
            current_version_id=article.current_version_id,
            title=cv.title if cv else "",
            abstract=cv.abstract if cv else None,
            keywords=cv.keywords or [] if cv else [],
            language=cv.language if cv else "en",
            doi=article.doi,
            pdf_path=cv.pdf_path if cv else "",
            journal_id=article.journal_id,
            status=ArticleStatus(cv.status) if cv else ArticleStatus.DRAFT,
            version_number=cv.version_number if cv else 1,
            is_visible=article.is_visible,
            view_count=article.view_count,
            download_count=article.download_count,
            creator_id=article.creator_id,
            updated_by_user_id=cv.updated_by_user_id if cv else None,
            published_at=cv.published_at if cv else None,
            created_at=article.created_at,
            updated_at=cv.updated_at if cv else None,
            authors=authors,
            journal=journal,
            citations=citations,
        )

    @staticmethod
    def _to_version_payload(version: ArticleVersion) -> ArticleVersionPayload:
        return ArticleVersionPayload(
            id=version.id,
            version_number=version.version_number,
            title=version.title,
            abstract=version.abstract,
            keywords=version.keywords or [],
            language=version.language,
            pdf_path=version.pdf_path,
            status=ArticleStatus(version.status),
            updated_by_user_id=version.updated_by_user_id,
            published_at=version.published_at,
            created_at=version.created_at,
            updated_at=version.updated_at,
        )

    # ------------------------------------------------------------------ #
    #  PRIVATE HELPERS
    # ------------------------------------------------------------------ #

    async def _get_article_or_fail(self, id: uuid.UUID) -> Article:
        article = await (
            self._article_repo.query()
            .where(Article.id == id)
            .with_current_version()
            .one_or_none(self._session)
        )
        if not article:
            raise NotFound("Article not found")
        return article

    async def _get_article_full_or_fail(self, id: uuid.UUID) -> Article:
        qb = (
            self._article_repo.query()
            .where(Article.id == id)
            .with_current_version()
            .with_authors()
            .with_journal()
            .with_citations()
        )
        qb._stmt = qb._stmt.execution_options(populate_existing=True)
        article = await qb.one_or_none(self._session)
        if not article:
            raise NotFound("Article not found")
        return article

    async def _assign_random_reviewer(self, version_id: uuid.UUID) -> None:
        from app.modules.users.models.user import User, RoleName
        from sqlalchemy import select

        random_reviewer = (
            await self._session.execute(
                select(User)
                .where(User.role_name == RoleName.REVIEWER)
                .order_by(func.random())
                .limit(1)
            )
        ).scalar_one_or_none()

        if not random_reviewer:
            raise BadRequest("No reviewers available")

        await self._assignment_repo.create({
            "id": uuid.uuid4(),
            "article_version_id": version_id,
            "reviewer_id": random_reviewer.id,
        })

    async def _check_is_author(self, article_id: uuid.UUID, user_id: uuid.UUID) -> None:
        link = await (
            self._article_authors_repo.query()
            .where(
                ArticleAuthors.article_id == article_id,
                ArticleAuthors.author_id == user_id,
            )
            .one_or_none(self._session)
        )
        if not link:
            raise Forbidden("You are not an author of this article")

    async def _check_not_already_author(self, article_id: uuid.UUID, author_id: uuid.UUID) -> None:
        link = await (
            self._article_authors_repo.query()
            .where(
                ArticleAuthors.article_id == article_id,
                ArticleAuthors.author_id == author_id,
            )
            .one_or_none(self._session)
        )
        if link:
            raise BadRequest("This user is already an author of the article")
