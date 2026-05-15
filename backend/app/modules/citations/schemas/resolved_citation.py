import uuid
from pydantic import BaseModel

from ..models import CitationMatchStatus

class ResolvedCitation(BaseModel):
    article_id: uuid.UUID | None = None
    doi: str | None = None
    raw_reference: str | None = None
    match_status: CitationMatchStatus