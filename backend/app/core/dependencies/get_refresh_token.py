from fastapi import Cookie
from app.core.exceptions import Unauthorized

async def get_refresh_token(
        refresh_token: str | None = Cookie(default=None)
) -> str:
    if not refresh_token:
        raise Unauthorized("Refresh token required")
    
    return refresh_token