import uuid
from pydantic import BaseModel

class JournalBriefPayload(BaseModel):
    id: uuid.UUID
    name: str