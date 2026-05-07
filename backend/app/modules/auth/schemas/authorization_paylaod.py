from pydantic import BaseModel
from .refresh_token import RefreshToken

class AuthorizationPaylaod(BaseModel):
    access_token: str
    refresh_token: RefreshToken