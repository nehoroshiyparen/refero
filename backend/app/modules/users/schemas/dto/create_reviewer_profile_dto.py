from pydantic import BaseModel, Field


class CreateReviewerProfileDTO(BaseModel):
    specialization: str = Field(max_length=255)
    degree: str | None = Field(default=None, max_length=100)
