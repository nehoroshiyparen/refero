from fastapi import Header, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from jose.jwt import ExpiredSignatureError, JWTError

from app.core.exceptions import Unauthorized
from app.core.security import security_bearer
from app.modules.auth.utils import decode_access_token
from app.modules.auth.schemas import AccessTokenPayload

async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> AccessTokenPayload:
    if not authorization:
        raise Unauthorized("Authorization header required")

    try:
        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise Unauthorized("Invalid auth scheme")

    except ValueError:
        raise Unauthorized("Invalid authorization header")

    try:
        payload = decode_access_token(token)

    except ExpiredSignatureError:
        raise Unauthorized("Access token expired")

    except JWTError:
        raise Unauthorized("Invalid access token")

    request.state.user = payload

    return payload