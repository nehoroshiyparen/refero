from fastapi import Depends
from typing import Iterable

from app.core.dependencies import get_current_user
from app.core.exceptions import Forbidden

from app.modules.users.models import RoleName
from app.modules.auth.schemas import AccessTokenPayload

def require_role(allowed_roles: Iterable[RoleName]):
    async def wrapper(user: AccessTokenPayload = Depends(get_current_user)) -> AccessTokenPayload:
        if not any(r in allowed_roles for r in user.roles):
            raise Forbidden()
        return user
    return wrapper