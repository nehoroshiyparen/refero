import uuid
from pydantic import BaseModel

class AuthorActionPayload(BaseModel):
    """Ответ после add/remove author."""
    message: str
    author_id: uuid.UUID | None = None