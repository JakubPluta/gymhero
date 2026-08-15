from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool = True
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    is_superuser: bool = False


class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    hashed_password: str
    is_superuser: bool = False


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=72)
    is_superuser: bool = False
