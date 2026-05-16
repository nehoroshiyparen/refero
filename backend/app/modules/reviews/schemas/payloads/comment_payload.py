import uuid
from datetime import datetime
from pydantic import BaseModel


class CommentPayload(BaseModel):
    id: uuid.UUID
    article_version_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
