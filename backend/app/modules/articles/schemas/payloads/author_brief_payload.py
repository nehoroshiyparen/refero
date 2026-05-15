import uuid
from datetime import datetime
from pydantic import BaseModel

class AuthorBriefPayload(BaseModel):
    author_id: uuid.UUID
    name: str
    email: str
    joined_at: datetime | None = None