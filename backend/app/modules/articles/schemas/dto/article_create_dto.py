import uuid
from pydantic import BaseModel, Field
from app.modules.articles.models.enum import ArticleStatus

class ArticleCreateDTO(BaseModel):
    title: str = Field(min_length=1, max_length=500)

    abstract: str | None = None

    keywords: list[str] = Field(default_factory=list)

    language: str = Field(default="en", min_length=2, max_length=5)

    pdf_path: str

    journal_id: uuid.UUID | None = None