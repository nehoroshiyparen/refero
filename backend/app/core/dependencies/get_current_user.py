from fastapi import Header, Request, Query
from jose.jwt import ExpiredSignatureError, JWTError

from app.core.exceptions import Unauthorized
from app.modules.auth.utils import decode_access_token
from app.modules.auth.schemas import AccessTokenPayload


async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
) -> AccessTokenPayload:
    raw = authorization or token

    if not raw:
        raise Unauthorized("Authentication required")

    if raw == token:
        access_token = token
    else:
        try:
            scheme, access_token = raw.split()
            if scheme.lower() != "bearer":
                raise Unauthorized("Invalid auth scheme")
        except ValueError:
            raise Unauthorized("Invalid authorization header")

    try:
        payload = decode_access_token(access_token)

    except ExpiredSignatureError:
        raise Unauthorized("Access token expired")

    except JWTError:
        raise Unauthorized("Invalid access token")

    request.state.user = payload

    return payload
