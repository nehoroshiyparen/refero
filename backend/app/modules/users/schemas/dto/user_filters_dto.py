from pydantic import BaseModel, Field

from ...models import RoleName

class UserFiltersDTO(BaseModel):
    role_name: RoleName | None = None
    query: str | None = Field(default=None, description="Search by username, email or full name")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
