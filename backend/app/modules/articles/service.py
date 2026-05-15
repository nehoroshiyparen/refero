import uuid

from app.core.base import BaseService
from app.core.exceptions import NotFound, Forbidden, BadRequest
from app.core.responses import PaginationMeta

from .repositories import (
    ArticleRepository,
    ArticleAuthorsRepository,
    ArticleApprovalsRepository,
)
from .models.article import Article
from .models.article_authors import ArticleAuthors
from .models.enum import ArticleStatus, ApprovalStatus
from .schemas import (
    ArticleCreateDTO,
    ArticleUpdateDTO,
    ArticleFiltersDTO,
    AddAuthorDTO,
    ArticlePayload,
    ArticleFullPayload,
    AuthorBriefPayload,
    JournalBriefPayload,
    ApprovalSubmissionPayload,
    AuthorActionPayload,
)


class ArticleService(BaseService):
    def __init__(self, session):
        super().__init__(session)
        self._article_repo = ArticleRepository(self._session)
        self._article_approvals_repo = ArticleApprovalsRepository(self._session)
        self._article_authors_repo = ArticleAuthorsRepository(self._session)

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
        )

        total = await qb.count(self._session)
        items = await qb.limit(filters.limit).offset(filters.offset).all(self._session)

        payloads = [self._to_payload(a) for a in items]
        meta = PaginationMeta(total=total, limit=filters.limit, offset=filters.offset)

        return payloads, meta

    async def get_article_by_id(self, id: uuid.UUID) -> ArticleFullPayload:
        article = await self._get_article_full_or_fail(id)
        await self._article_repo.update(id, {"view_count": article.view_count + 1})
        return self._to_full_payload(article)

    # ------------------------------------------------------------------ #
    #  CREATE / UPDATE / DELETE
    # ------------------------------------------------------------------ #

    async def create_article(
        self,
        dto: ArticleCreateDTO,
        user_id: uuid.UUID,
    ) -> ArticlePayload:
        article = await self._article_repo.create({
            "id": str(uuid.uuid4()),
            "title": dto.title,
            "abstract": dto.abstract,
            "keywords": dto.keywords,
            "language": dto.language,
            "pdf_path": dto.pdf_path,
            "journal_id": str(dto.journal_id) if dto.journal_id else None,
            "status": ArticleStatus.DRAFT.value,
            "creator_id": str(user_id),
            "updated_by_user_id": str(user_id),
        })

        # Создатель = первый автор
        await self._article_authors_repo.create({
            "id": str(uuid.uuid4()),
            "article_id": str(article.id),
            "author_id": str(user_id),
        })

        return self._to_payload(article)

    async def update_article(
        self,
        id: uuid.UUID,
        dto: ArticleUpdateDTO,
        user_id: uuid.UUID,
    ) -> ArticlePayload:
        article = await self._get_article_or_fail(id)

        if article.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only update articles in draft status")

        await self._check_is_author(id, user_id)

        data: dict[str, str | list[str]] = {"updated_by_user_id": str(user_id)}
        for field in ("title", "abstract", "language", "pdf_path"):
            value = getattr(dto, field, None)
            if value is not None:
                data[field] = value

        if dto.keywords is not None:
            data["keywords"] = dto.keywords
        if dto.journal_id is not None:
            data["journal_id"] = str(dto.journal_id)

        updated = await self._article_repo.update(id, data)
        return self._to_payload(updated)

    async def delete_article(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        article = await self._get_article_or_fail(id)

        if article.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only delete articles in draft status")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can delete it")

        await self._article_repo.delete(id)

    # ------------------------------------------------------------------ #
    #  APPROVAL WORKFLOW
    # ------------------------------------------------------------------ #

    async def submit_for_approval(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ApprovalSubmissionPayload:
        article = await self._get_article_or_fail(id)

        if article.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only submit draft articles for approval")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can submit for approval")

        # Соавторы без создателя
        co_authors = await (
            self._article_authors_repo.query()
            .where(
                ArticleAuthors.article_id == id,
                ArticleAuthors.author_id != user_id,
            )
            .all(self._session)
        )

        if not co_authors:
            # Нет соавторов → сразу в REVIEW
            await self._article_repo.update(id, {
                "status": ArticleStatus.REVIEW.value,
            })
            return ApprovalSubmissionPayload(
                message="Article submitted for review (no co-authors to approve)"
            )

        # Создаём pending-апрувы для каждого соавтора
        for co_author in co_authors:
            await self._article_approvals_repo.create({
                "id": str(uuid.uuid4()),
                "article_id": str(id),
                "approver_id": str(co_author.author_id),
                "status": ApprovalStatus.PENDING.value,
            })

        await self._article_repo.update(id, {
            "status": ArticleStatus.PENDING_APPROVAL.value,
        })

        return ApprovalSubmissionPayload(
            message=f"Article submitted for approval. Waiting for {len(co_authors)} co-author(s)"
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

        if article.status != ArticleStatus.DRAFT:
            raise BadRequest("Can only add authors to draft articles")

        if article.creator_id != user_id:
            raise Forbidden("Only the article creator can add co-authors")

        await self._check_not_already_author(article_id, dto.author_id)

        await self._article_authors_repo.create({
            "id": str(uuid.uuid4()),
            "article_id": str(article_id),
            "author_id": str(dto.author_id),
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

        if article.status != ArticleStatus.DRAFT:
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

        if not article.pdf_path:
            raise NotFound("Article has no PDF file")

        await self._article_repo.update(id, {"download_count": article.download_count + 1})

        return article.pdf_path

    # ------------------------------------------------------------------ #
    #  MAPPER HELPERS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_payload(article: Article) -> ArticlePayload:
        return ArticlePayload(
            id=article.id,
            title=article.title,
            abstract=article.abstract,
            keywords=article.keywords or [],
            language=article.language,
            doi=article.doi,
            pdf_path=article.pdf_path,
            journal_id=article.journal_id,
            status=ArticleStatus(article.status),
            view_count=article.view_count,
            download_count=article.download_count,
            creator_id=article.creator_id if hasattr(article, "creator_id") else None,
            updated_by_user_id=article.updated_by_user_id,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
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

        return ArticleFullPayload(
            id=article.id,
            title=article.title,
            abstract=article.abstract,
            keywords=article.keywords or [],
            language=article.language,
            doi=article.doi,
            pdf_path=article.pdf_path,
            journal_id=article.journal_id,
            status=ArticleStatus(article.status),
            view_count=article.view_count,
            download_count=article.download_count,
            creator_id=article.creator_id if hasattr(article, "creator_id") else None,
            updated_by_user_id=article.updated_by_user_id,
            published_at=article.published_at,
            created_at=article.created_at,
            updated_at=article.updated_at,
            authors=authors,
            journal=journal,
        )
    
    # ------------------------------------------------------------------ #
    #  PRIVATE HELPERS
    # ------------------------------------------------------------------ #
    
    async def _get_article_or_fail(self, id: uuid.UUID) -> Article:
        article = await (
            self._article_repo.query()
            .where(Article.id == id)
            .one_or_none(self._session)
        )
        if not article:
            raise NotFound("Article not found")
        return article
    
    async def _get_article_full_or_fail(self, id: uuid.UUID) -> Article:
        article = await (
            self._article_repo.query()
            .where(Article.id == id)
            .with_authors()
            .with_journal()
            .one_or_none(self._session)
        )
        if not article:
            raise NotFound("Article not found")
        return article
    
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