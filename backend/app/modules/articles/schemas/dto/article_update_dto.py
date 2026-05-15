import uuid
from pydantic import BaseModel, Field

from app.modules.citations.schemas import CitationInput

class ArticleUpdateDTO(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)

    abstract: str | None = None

    keywords: list[str] | None = None

    language: str | None = Field(default=None, min_length=2, max_length=5)

    pdf_path: str | None = None

    journal_id: uuid.UUID | None = None

    citations: list[CitationInput] | None = None