import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base import BaseService
from app.core.exceptions import NotFound, BadRequest, Forbidden

from app.modules.articles.repositories import ArticleRepository
from app.modules.articles.models import Article, ArticleStatus

from .repository import CitationRepository, Citation
from .models import CitationMatchStatus
from .schemas import (
    CitationInput,
    ResolvedCitation
)

class CitationService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self._citation_repo = CitationRepository(self._session)
        self._article_repo = ArticleRepository(self._session)

    async def delete_citation(self, id: uuid.UUID, user_id: uuid.UUID):
        citation = await (
            self._citation_repo.query()
            .where(Citation.id == id)
            .one_or_none(self._session)
        )

        if not citation:
            raise NotFound("Citation not found")
        
        article = await (
            self._article_repo.query()
            .where(Article.id == citation.from_article_id)
            .one_or_none(self._session)
        )

        if not article:
            raise NotFound("Quoted article is not found")

        is_author = any(author.id == user_id for author in article.authors)

        if not is_author:
            raise Forbidden("Only article author can delete citations")

        await self._citation_repo.delete(citation.id)

    async def resolve_citations(
        self,
        from_article_id: uuid.UUID,
        citations: list[CitationInput]
    ):
        results = []

        for citation in citations:
            resolved = await self._resolve_one(citation)
            if not resolved:
                continue
            
            record = await self._citation_repo.create({
                "from_article_id": str(from_article_id),
                "to_article_id": str(resolved.article_id) if resolved.article_id else None,
                "doi": resolved.doi,
                "raw_reference": resolved.raw_reference,
                "match_status": resolved.match_status
            })
            results.append(record)
        
        return results

    async def count_citations(self, article_id: uuid.UUID) -> int:
        total = await (
            self._citation_repo.query()
            .where(Citation.to_article_id == article_id)
            .count(self._session)
        )
        return total

    async def replace_citations(
        self,
        from_article_id: uuid.UUID,
        citations: list[CitationInput],
    ):
        old = await (
            self._citation_repo.query()
            .where(Citation.from_article_id == from_article_id)
            .all(self._session)
        )
        for c in old:
            await self._citation_repo.delete(c.id)

        return await self.resolve_citations(from_article_id, citations)

    async def _resolve_one(self, citation: CitationInput):
        if citation.article_id:
            article = await (
                self._article_repo.query()
                .where(Article.id == citation.article_id)
                .one_or_none(self._session)
            )

            if not article:
                raise NotFound("Cited article not found")
            
            if article.status != ArticleStatus.PUBLISHED:
                raise BadRequest("You can only cite published articles")
            
            return ResolvedCitation(
                article_id=article.id,
                doi=citation.doi,
                raw_reference=citation.raw_reference,
                match_status=CitationMatchStatus.LINKED
            )
        if citation.doi:
            article = await (
                self._article_repo.query()
                .where(Article.doi == citation.doi)
                .one_or_none(self._session)
            )

            if article and article.status != ArticleStatus.PUBLISHED:
                raise BadRequest("You can only cite published articles")
            
            return ResolvedCitation(
                article_id=article.id if article else None,
                doi=citation.doi,
                raw_reference=citation.raw_reference,
                match_status=CitationMatchStatus.PENDING if not article else CitationMatchStatus.LINKED
            )
        if citation.raw_reference:
            return ResolvedCitation(
                article_id=None,
                doi=None,
                raw_reference=citation.raw_reference,
                match_status=CitationMatchStatus.EXTERNAL,
            )
        return None