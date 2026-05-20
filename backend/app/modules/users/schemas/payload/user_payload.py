import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from ...models import RoleName
from .author_profile_payload import AuthorProfilePayload
from .reviewer_profile_payload import ReviewerProfilePayload

class UserPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    username: str
    email: str

    full_name: str

    avatar_url: str | None

    is_active: bool

    roles: list[RoleName]

    created_at: datetime
    updated_at: datetime

    author_profile: Optional[AuthorProfilePayload]
    reviewer_profile: Optional[ReviewerProfilePayload]