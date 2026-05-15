from pydantic import BaseModel, Field

class UpdateReviewDTO(BaseModel):
    comment: str | None = Field(default=None, max_length=5000)
