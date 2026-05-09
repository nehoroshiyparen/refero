from fastapi import Cookie
from app.core.exceptions import Forbidden

async def unathorized_only(
        refresh_token: str | None = Cookie(default=None)
) -> None:
    if refresh_token:
        raise Forbidden("Unauthorized access only")
    
    return