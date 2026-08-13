from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool = True
    full_name: str | None = None


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
    password: str | None = None
    is_superuser: bool = False
