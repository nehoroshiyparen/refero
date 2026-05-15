import uuid
from pydantic import  BaseModel

class CitationInput(BaseModel):
    doi: str | None = None

    article_id: uuid.UUID | None = None

    raw_reference: str | None = None