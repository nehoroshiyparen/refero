import uuid
from sqlalchemy.orm import selectinload
from sqlalchemy import select, exists, or_

from app.infrastructure.database import BaseQueryBuilder
from ..models import Article, ArticleAuthors, ArticleStatus
from app.modules.citations.models import Citation

class ArticleQueryBuilder(BaseQueryBuilder[Article]):
    def __init__(self, model):
        super().__init__(model)

    def filter_text(self, query: str | None) -> "ArticleQueryBuilder":
        if query:
            pattern = f"%{query}%"
            self._stmt = self._stmt.where(
                or_(
                    Article.title.ilike(pattern),
                    Article.abstract.ilike(pattern),
                )
            )
        return self

    def filter_status(self, status: ArticleStatus | None) -> "ArticleQueryBuilder":
        if status is not None:
            self._stmt = self._stmt.where(Article.status == status)
        return self

    def filter_journal(self, journal_id: uuid.UUID | None) -> "ArticleQueryBuilder":
        if journal_id is not None:
            self._stmt = self._stmt.where(Article.journal_id == journal_id)
        return self

    def filter_language(self, language: str | None) -> "ArticleQueryBuilder":
        if language is not None:
            self._stmt = self._stmt.where(Article.language == language)
        return self

    def filter_author(self, author_id: uuid.UUID | None) -> "ArticleQueryBuilder":
        if author_id is not None:
            # EXISTS — без дублирования строк от JOIN
            subq = (
                select(ArticleAuthors)
                .where(
                    ArticleAuthors.article_id == Article.id,
                    ArticleAuthors.author_id == author_id,
                )
                .correlate(Article)
            )
            self._stmt = self._stmt.where(exists(subq))
        return self

    def filter_keywords(self, keywords: list[str] | None) -> "ArticleQueryBuilder":
        if keywords:
            # Статья содержит ЛЮБОЕ из ключевых слов (OR)
            conditions = [Article.keywords.any(kw) for kw in keywords]
            self._stmt = self._stmt.where(or_(*conditions))
        return self
    
    def with_authors(self) -> "ArticleQueryBuilder":
        """Подгрузить авторов (для детальной страницы)."""
        self._stmt = self._stmt.options(
            selectinload(Article.authors).selectinload(ArticleAuthors.author),
        )
        return self

    def with_journal(self) -> "ArticleQueryBuilder":
        """Подгрузить журнал."""
        self._stmt = self._stmt.options(selectinload(Article.journal))
        return self

    def with_citations(self) -> "ArticleQueryBuilder":
        """Подгрузить исходящие цитирования."""
        self._stmt = self._stmt.options(selectinload(Article.citations_from))
        return self