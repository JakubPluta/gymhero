from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class Payload(BaseModel):
    user_id: Optional[int]
