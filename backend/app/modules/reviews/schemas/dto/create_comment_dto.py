import uuid
from pydantic import BaseModel, Field


class CreateCommentDTO(BaseModel):
    article_version_id: uuid.UUID
    content: str = Field(min_length=1, max_length=10000)
