import uuid
from datetime import datetime
from pydantic import BaseModel

from ..models import CitationMatchStatus

class CitationBriefPayload(BaseModel):
    id: uuid.UUID
    to_article_id: uuid.UUID | None = None
    doi: str | None = None
    raw_reference: str | None = None
    match_status: CitationMatchStatus
    created_at: datetime | None = None
