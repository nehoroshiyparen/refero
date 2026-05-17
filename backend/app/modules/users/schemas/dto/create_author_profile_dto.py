from pydantic import BaseModel, Field
from typing import Optional

class CreateAuthorProfileDTO(BaseModel):
    organization: Optional[str] = Field(default=None, max_length=255)
    position: Optional[str] = Field(default=None, max_length=255)

    degree: Optional[str] = Field(default=None, max_length=100)
    orcid: str = Field(max_length=50)

    bio: Optional[str] = Field(default=None)