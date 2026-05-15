from pydantic import BaseModel, Field

class CreateJournalDTO(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issn: str | None = Field(default=None, max_length=20)
    description: str | None = None
