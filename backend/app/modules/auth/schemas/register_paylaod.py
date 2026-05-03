from pydantic import BaseModel
from .refresh_token import RefreshToken

class RegisterPaylaod(BaseModel):
    access_token: str
    refresh_token: RefreshToken