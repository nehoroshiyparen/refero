from pydantic import BaseModel, ConfigDict

class ReviewerProfilePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    specialization: str | None
    degree: str | None