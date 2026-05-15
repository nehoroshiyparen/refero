import uuid
from datetime import datetime
from pydantic import BaseModel

class JournalPayload(BaseModel):
    id: uuid.UUID
    name: str
    issn: str | None = None
    description: str | None = None
    created_at: datetime | None = None
