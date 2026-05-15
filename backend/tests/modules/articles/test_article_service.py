import uuid
import pytest
import pytest_asyncio

from sqlalchemy import text

from app.modules.articles.service import ArticleService
from app.modules.articles.models.enum import ArticleStatus, ApprovalStatus
from app.modules.articles.schemas import (
    ArticleCreateDTO,
    ArticleUpdateDTO,
    ArticleFiltersDTO,
    AddAuthorDTO,
)
from app.modules.citations.schemas import CitationInput
from app.core.exceptions import NotFound, Forbidden, BadRequest

pytestmark = pytest.mark.asyncio

# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture
def service(db_session):
    return ArticleService(db_session)


@pytest_asyncio.fixture(loop_scope="session")
async def draft_article(service, test_user) -> dict:
    """Создаёт черновик статьи и возвращает payload."""
    dto = ArticleCreateDTO(
        title="Test Article",
        abstract="Test abstract",
        keywords=["test", "article"],
        language="en",
        pdf_path="/uploads/test.pdf",
    )
    result = await service.create_article(dto, user_id=test_user["id"])
    return result


# ── CREATE ────────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestCreateArticle:

    async def test_create_article_success(self, service, test_user):
        dto = ArticleCreateDTO(
            title="My Article",
            abstract="Some abstract",
            keywords=["python", "fastapi"],
            language="en",
            pdf_path="/uploads/paper.pdf",
        )
        result = await service.create_article(dto, user_id=test_user["id"])

        assert result.title == "My Article"
        assert result.abstract == "Some abstract"
        assert result.keywords == ["python", "fastapi"]
        assert result.language == "en"
        assert result.status == ArticleStatus.DRAFT
        assert result.creator_id == test_user["id"]
        assert result.view_count == 0
        assert result.download_count == 0

    async def test_create_article_with_journal(self, service, test_user, db_session):
        # Создаём журнал
        journal_id = uuid.uuid4()
        await db_session.execute(
            text("INSERT INTO journals (id, name) VALUES (:id, :name)"),
            {"id": str(journal_id), "name": "Test Journal"},
        )
        await db_session.flush()

        dto = ArticleCreateDTO(
            title="Article with Journal",
            pdf_path="/uploads/paper.pdf",
            journal_id=journal_id,
        )
        result = await service.create_article(dto, user_id=test_user["id"])

        assert result.journal_id == journal_id

    async def test_create_article_creator_is_author(self, service, test_user):
        dto = ArticleCreateDTO(
            title="Check Author",
            pdf_path="/uploads/paper.pdf",
        )
        result = await service.create_article(dto, user_id=test_user["id"])

        # Проверяем что создатель добавлен в авторы
        authors_result = await service._article_authors_repo.query().where(
            service._article_authors_repo._model.article_id == result.id,
        ).one_or_none(db_session := service._session)

        assert authors_result is not None
        assert authors_result.author_id == test_user["id"]

    async def test_create_article_with_citations(self, service, test_user):
        dto = ArticleCreateDTO(
            title="Article with Citations",
            pdf_path="/uploads/paper.pdf",
            citations=[
                CitationInput(raw_reference="External ref 1"),
                CitationInput(raw_reference="External ref 2"),
            ],
        )
        result = await service.create_article(dto, user_id=test_user["id"])

        assert len(result.citations) == 2
        assert result.citations[0].match_status.value == "external"

    async def test_create_article_journal_not_found(self, service, test_user):
        dto = ArticleCreateDTO(
            title="Bad Journal",
            pdf_path="/uploads/paper.pdf",
            journal_id=uuid.uuid4(),
        )

        with pytest.raises(NotFound, match="journal"):
            await service.create_article(dto, user_id=test_user["id"])


# ── GET BY ID ─────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestGetArticleById:

    async def test_get_article_by_id_success(self, service, draft_article):
        result = await service.get_article_by_id(draft_article.id)

        assert result.id == draft_article.id
        assert result.title == "Test Article"
        assert result.view_count == 1  # инкрементится при получении

    async def test_get_article_by_id_increments_view_count(self, service, draft_article):
        await service.get_article_by_id(draft_article.id)
        await service.get_article_by_id(draft_article.id)

        result = await service.get_article_by_id(draft_article.id)
        assert result.view_count == 3

    async def test_get_article_by_id_not_found(self, service):
        with pytest.raises(NotFound):
            await service.get_article_by_id(uuid.uuid4())


# ── GET LIST ──────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestGetArticles:

    async def test_get_articles_empty(self, service):
        filters = ArticleFiltersDTO()
        items, meta = await service.get_articles(filters)

        # Может быть не 0 если другие тесты успели, но структура верная
        assert isinstance(items, list)
        assert isinstance(meta.total, int)

    async def test_get_articles_with_status_filter(self, service, draft_article):
        filters = ArticleFiltersDTO(status=ArticleStatus.DRAFT)
        items, meta = await service.get_articles(filters)

        assert len(items) >= 1
        assert all(a.status == ArticleStatus.DRAFT for a in items)

    async def test_get_articles_with_language_filter(self, service, draft_article):
        filters = ArticleFiltersDTO(language="en")
        items, meta = await service.get_articles(filters)

        assert len(items) >= 1

    async def test_get_articles_with_text_filter(self, service, draft_article):
        filters = ArticleFiltersDTO(query="Test")
        items, meta = await service.get_articles(filters)

        assert len(items) >= 1

    async def test_get_articles_pagination(self, service, draft_article):
        filters = ArticleFiltersDTO(limit=1, offset=0)
        items, meta = await service.get_articles(filters)

        assert len(items) <= 1
        assert meta.limit == 1
        assert meta.offset == 0


# ── UPDATE ────────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestUpdateArticle:

    async def test_update_article_success(self, service, draft_article, test_user):
        dto = ArticleUpdateDTO(title="Updated Title", abstract="New abstract")
        result = await service.update_article(
            draft_article.id, dto, user_id=test_user["id"]
        )

        assert result.title == "Updated Title"
        assert result.abstract == "New abstract"
        assert result.updated_by_user_id == test_user["id"]

    async def test_update_article_not_author(self, service, draft_article, test_coauthor):
        dto = ArticleUpdateDTO(title="Hacked Title")

        with pytest.raises(Forbidden):
            await service.update_article(
                draft_article.id, dto, user_id=test_coauthor["id"]
            )

    async def test_update_article_not_draft(self, service, draft_article, test_user, db_session):
        # Меняем статус напрямую
        await db_session.execute(
            text("UPDATE articles SET status = 'REVIEW' WHERE id = :id"),
            {"id": str(draft_article.id)},
        )
        await db_session.flush()

        dto = ArticleUpdateDTO(title="Should Fail")

        with pytest.raises(BadRequest, match="draft"):
            await service.update_article(
                draft_article.id, dto, user_id=test_user["id"]
            )

    async def test_update_article_partial(self, service, draft_article, test_user):
        dto = ArticleUpdateDTO(title="Only Title Changed")
        result = await service.update_article(
            draft_article.id, dto, user_id=test_user["id"]
        )

        assert result.title == "Only Title Changed"
        assert result.abstract == "Test abstract"  # не изменилось

    async def test_update_article_not_found(self, service, test_user):
        dto = ArticleUpdateDTO(title="Ghost")

        with pytest.raises(NotFound):
            await service.update_article(uuid.uuid4(), dto, user_id=test_user["id"])

    async def test_update_article_with_citations(self, service, draft_article, test_user):
        dto = ArticleUpdateDTO(
            citations=[CitationInput(raw_reference="Added via update")],
        )
        result = await service.update_article(
            draft_article.id, dto, user_id=test_user["id"],
        )

        assert len(result.citations) == 1
        assert result.citations[0].raw_reference == "Added via update"

    async def test_update_article_journal_not_found(
        self, service, draft_article, test_user
    ):
        dto = ArticleUpdateDTO(journal_id=uuid.uuid4())

        with pytest.raises(NotFound, match="journal"):
            await service.update_article(
                draft_article.id, dto, user_id=test_user["id"],
            )

    async def test_update_article_clear_journal(
        self, service, draft_article, test_user, db_session
    ):
        journal_id = uuid.uuid4()
        await db_session.execute(
            text("INSERT INTO journals (id, name) VALUES (:id, :name)"),
            {"id": str(journal_id), "name": "Temp Journal"},
        )
        await db_session.flush()

        await db_session.execute(
            text("UPDATE articles SET journal_id = :jid WHERE id = :id"),
            {"jid": str(journal_id), "id": str(draft_article.id)},
        )
        await db_session.flush()

        dto = ArticleUpdateDTO(journal_id=None)
        result = await service.update_article(
            draft_article.id, dto, user_id=test_user["id"],
        )

        assert result.journal_id is None


# ── DELETE ────────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestDeleteArticle:

    async def test_delete_article_success(self, service, draft_article, test_user):
        await service.delete_article(draft_article.id, user_id=test_user["id"])

        with pytest.raises(NotFound):
            await service.get_article_by_id(draft_article.id)

    async def test_delete_article_not_creator(self, service, draft_article, test_coauthor):
        with pytest.raises(Forbidden, match="creator"):
            await service.delete_article(
                draft_article.id, user_id=test_coauthor["id"]
            )

    async def test_delete_article_not_draft(self, service, draft_article, test_user, db_session):
        await db_session.execute(
            text("UPDATE articles SET status = 'REVIEW' WHERE id = :id"),
            {"id": str(draft_article.id)},
        )
        await db_session.flush()

        with pytest.raises(BadRequest, match="draft"):
            await service.delete_article(draft_article.id, user_id=test_user["id"])

    async def test_delete_article_not_found(self, service, test_user):
        with pytest.raises(NotFound):
            await service.delete_article(uuid.uuid4(), user_id=test_user["id"])


# ── SUBMIT FOR APPROVAL ──────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestSubmitForApproval:

    async def test_submit_no_coauthors(self, service, draft_article, test_user):
        result = await service.submit_for_approval(
            draft_article.id, user_id=test_user["id"]
        )

        assert "review" in result.message.lower()

        # Статус должен быть REVIEW (нет соавторов → сразу в review)
        article = await service.get_article_by_id(draft_article.id)
        assert article.status == ArticleStatus.REVIEW

    async def test_submit_with_coauthors(
        self, service, draft_article, test_user, test_coauthor
    ):
        # Добавляем соавтора
        dto = AddAuthorDTO(author_id=test_coauthor["id"])
        await service.add_author(draft_article.id, dto, user_id=test_user["id"])

        # Отправляем на апрув
        result = await service.submit_for_approval(
            draft_article.id, user_id=test_user["id"]
        )

        assert "co-author" in result.message.lower()

        article = await service.get_article_by_id(draft_article.id)
        assert article.status == ArticleStatus.PENDING_APPROVAL

    async def test_submit_not_creator(self, service, draft_article, test_coauthor):
        with pytest.raises(Forbidden, match="creator"):
            await service.submit_for_approval(
                draft_article.id, user_id=test_coauthor["id"]
            )

    async def test_submit_not_draft(self, service, draft_article, test_user, db_session):
        await db_session.execute(
            text("UPDATE articles SET status = 'REVIEW' WHERE id = :id"),
            {"id": str(draft_article.id)},
        )
        await db_session.flush()

        with pytest.raises(BadRequest, match="draft"):
            await service.submit_for_approval(
                draft_article.id, user_id=test_user["id"]
            )


# ── ADD / DELETE AUTHOR ──────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestAuthorManagement:

    async def test_add_author_success(
        self, service, draft_article, test_user, test_coauthor
    ):
        dto = AddAuthorDTO(author_id=test_coauthor["id"])
        result = await service.add_author(
            draft_article.id, dto, user_id=test_user["id"]
        )

        assert result.author_id == test_coauthor["id"]

    async def test_add_author_not_creator(
        self, service, draft_article, test_coauthor
    ):
        dto = AddAuthorDTO(author_id=uuid.uuid4())

        with pytest.raises(Forbidden, match="creator"):
            await service.add_author(
                draft_article.id, dto, user_id=test_coauthor["id"]
            )

    async def test_add_author_already_exists(
        self, service, draft_article, test_user
    ):
        # Создатель уже автор
        dto = AddAuthorDTO(author_id=test_user["id"])

        with pytest.raises(BadRequest, match="already"):
            await service.add_author(
                draft_article.id, dto, user_id=test_user["id"]
            )

    async def test_add_author_not_draft(
        self, service, draft_article, test_user, test_coauthor, db_session
    ):
        await db_session.execute(
            text("UPDATE articles SET status = 'REVIEW' WHERE id = :id"),
            {"id": str(draft_article.id)},
        )
        await db_session.flush()

        dto = AddAuthorDTO(author_id=test_coauthor["id"])

        with pytest.raises(BadRequest, match="draft"):
            await service.add_author(
                draft_article.id, dto, user_id=test_user["id"]
            )

    async def test_delete_author_success(
        self, service, draft_article, test_user, test_coauthor
    ):
        # Сначала добавляем
        dto = AddAuthorDTO(author_id=test_coauthor["id"])
        await service.add_author(draft_article.id, dto, user_id=test_user["id"])

        # Потом удаляем
        result = await service.delete_author(
            draft_article.id, test_coauthor["id"], user_id=test_user["id"]
        )

        assert "successfully" in result.message.lower()

    async def test_delete_author_cannot_remove_creator(
        self, service, draft_article, test_user
    ):
        with pytest.raises(BadRequest, match="creator"):
            await service.delete_author(
                draft_article.id, test_user["id"], user_id=test_user["id"]
            )

    async def test_delete_author_not_creator(
        self, service, draft_article, test_coauthor
    ):
        with pytest.raises(Forbidden, match="creator"):
            await service.delete_author(
                draft_article.id, test_coauthor["id"], user_id=test_coauthor["id"]
            )

    async def test_delete_author_not_found(
        self, service, draft_article, test_user, test_coauthor
    ):
        # test_coauthor не добавлен как автор статьи
        with pytest.raises(NotFound):
            await service.delete_author(
                draft_article.id, test_coauthor["id"], user_id=test_user["id"]
            )


# ── DOWNLOAD ──────────────────────────────────────────────────

@pytest.mark.asyncio(loop_scope="session")
class TestDownloadArticle:

    async def test_download_article_success(self, service, draft_article):
        pdf_path = await service.download_article(draft_article.id)

        assert pdf_path == "/uploads/test.pdf"

    async def test_download_article_increments_count(self, service, draft_article):
        await service.download_article(draft_article.id)
        await service.download_article(draft_article.id)

        result = await service.get_article_by_id(draft_article.id)
        assert result.download_count == 2

    async def test_download_article_not_found(self, service):
        with pytest.raises(NotFound):
            await service.download_article(uuid.uuid4())