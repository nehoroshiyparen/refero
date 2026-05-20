import uuid
from datetime import datetime
from pydantic import BaseModel


class CommentPayload(BaseModel):
    id: uuid.UUID
    article_version_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str = ""
    content: str
    created_at: datetime
