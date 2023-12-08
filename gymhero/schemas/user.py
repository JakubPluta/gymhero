from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: bool = True
    full_name: Optional[str] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    is_superuser: bool = False


class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    hashed_password: str
    is_superuser: bool = False


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_superuser: bool = False
