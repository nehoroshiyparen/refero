from pydantic import BaseModel
from datetime import datetime, timedelta

class RefreshToken(BaseModel):
    token_hash: str
    expires_at: datetime