import uuid
from datetime import datetime
from pydantic import BaseModel
from ...models import ArticleStatus


class ArticleVersionPayload(BaseModel):
    id: uuid.UUID
    version_number: int
    title: str
    abstract: str | None = None
    keywords: list[str] = []
    language: str = "en"
    pdf_path: str
    pdf_url: str | None = None
    status: ArticleStatus
    updated_by_user_id: uuid.UUID | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
