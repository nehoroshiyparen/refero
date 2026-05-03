from pydantic import BaseModel, EmailStr, model_validator

class LoginRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str

    @model_validator(mode="after")
    def username_or_email_required(self) -> "LoginRequest":
        if not self.username and not self.email:
            raise ValueError("Either username or email must be provided")
        return self