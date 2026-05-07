from fastapi import Header, Request
from jose.jwt import ExpiredSignatureError, JWTError
from app.core.exceptions import Unauthorized
from app.modules.auth.utils import decode_access_token


async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
) -> dict["id": int, "role": str]:
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