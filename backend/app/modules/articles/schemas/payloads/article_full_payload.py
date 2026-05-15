from app.modules.citations.schemas import CitationBriefPayload

from .author_brief_payload import AuthorBriefPayload
from .journal_brief_payload import JournalBriefPayload
from .article_payload import ArticlePayload

class ArticleFullPayload(ArticlePayload):
    """Детальный payload — для get_by_id, с авторами и журналом."""
    authors: list[AuthorBriefPayload] = []
    journal: JournalBriefPayload | None = None
    citations: list[CitationBriefPayload] = []