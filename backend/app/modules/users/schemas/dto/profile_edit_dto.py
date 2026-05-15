from pydantic import BaseModel


class AuthorProfileFields(BaseModel):
    organization: str | None = None
    position: str | None = None
    degree: str | None = None
    orcid: str | None = None
    bio: str | None = None


class ReviewerProfileFields(BaseModel):
    specialization: str | None = None
    degree: str | None = None


class ProfileEditDTO(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None

    author: AuthorProfileFields | None = None
    reviewer: ReviewerProfileFields | None = None
