import uuid
from pydantic import BaseModel, Field
from ...models import ArticleStatus

class ArticleFiltersDTO(BaseModel):
    query: str | None = Field(default=None, description="Search by title or abstract")

    status: ArticleStatus | None = None

    journal_id: uuid.UUID | None = None

    author_id: uuid.UUID | None = None

    language: str | None = None

    keywords: list[str] | None = None

    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)