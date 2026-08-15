from pydantic import BaseModel, EmailStr, Field, SecretStr


class Token(BaseModel):
    """Bearer access + refresh tokens."""

    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: int | None = None
    type: str | None = None
    ver: int | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRegister(BaseModel):
    email: EmailStr
    # max_length guards bcrypt's 72-byte truncation (char count; ASCII == bytes).
    password: SecretStr = Field(min_length=8, max_length=72)
    full_name: str | None = Field(default=None, max_length=255)
