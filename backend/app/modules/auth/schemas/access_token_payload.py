from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator
from app.modules.users.models import RoleName

class AccessTokenPayload(BaseModel):
    id: UUID
    roles: list[RoleName] = []

    model_config=ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def migrate_role_to_roles(cls, data):
        if isinstance(data, dict) and "role" in data and "roles" not in data:
            data["roles"] = [data["role"]]
        return data