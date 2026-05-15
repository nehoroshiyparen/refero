from pydantic import BaseModel

class AuthorizationResponse(BaseModel):
    access_token: str