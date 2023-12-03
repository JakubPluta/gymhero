from typing import Optional

from pydantic import BaseModel, EmailStr


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

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    hashed_password: str
    is_superuser: bool = False


class UserUpdate(UserBase):
    password: Optional[str] = None
    is_superuser: bool = False
