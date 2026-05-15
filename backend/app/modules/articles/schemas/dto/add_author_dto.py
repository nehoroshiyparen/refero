import uuid
from pydantic import BaseModel

class AddAuthorDTO(BaseModel):
    author_id: uuid.UUID