from pydantic import BaseModel, Field

class UpdateJournalDTO(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    issn: str | None = None
    description: str | None = None
