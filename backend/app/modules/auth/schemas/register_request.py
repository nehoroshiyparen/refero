from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str

    @field_validator("username")
    @classmethod
    def username_must_be_latin(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only latin letters, digits and underscores")
        return v