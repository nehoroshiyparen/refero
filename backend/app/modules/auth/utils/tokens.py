import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings
from ..schemas import RefreshToken, AccessTokenPayload

def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> AccessTokenPayload:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    return AccessTokenPayload(
        **payload
    )

def generate_refresh_token() -> RefreshToken:
    return RefreshToken(
        token_hash=secrets.token_urlsafe(64),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()