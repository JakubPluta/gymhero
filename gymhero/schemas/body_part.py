import datetime
from typing import List, Optional

from pydantic import BaseModel


class BodyPartBase(BaseModel):
    name: str


class BodyPartCreate(BodyPartBase):
    pass


class BodyPartUpdate(BodyPartBase):
    name: Optional[str]


class BodyPartInDB(BodyPartBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class BodyPartsInDB(BaseModel):
    results: List[BodyPartInDB]
