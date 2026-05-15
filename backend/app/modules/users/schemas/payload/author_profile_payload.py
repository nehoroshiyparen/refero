from pydantic import BaseModel, ConfigDict

class AuthorProfilePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization: str | None
    position: str | None

    degree: str | None
    orcid: str | None

    bio: str | None