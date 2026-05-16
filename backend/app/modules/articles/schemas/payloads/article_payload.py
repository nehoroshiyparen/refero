import uuid
from datetime import datetime
from pydantic import BaseModel
from ...models import ArticleStatus

class ArticlePayload(BaseModel):
    id: uuid.UUID
    current_version_id: uuid.UUID | None = None
    title: str
    abstract: str | None = None
    keywords: list[str] = []
    language: str = "en"
    doi: str | None = None
    pdf_path: str
    journal_id: uuid.UUID | None = None
    status: ArticleStatus
    version_number: int = 1
    is_visible: bool = True
    view_count: int = 0
    download_count: int = 0
    creator_id: uuid.UUID | None = None
    updated_by_user_id: uuid.UUID | None = None
    published_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None