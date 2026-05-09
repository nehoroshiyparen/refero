from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.modules.users.models import RoleName

class AccessTokenPayload(BaseModel):
    id: UUID
    role: RoleName

    model_config=ConfigDict(extra="allow")