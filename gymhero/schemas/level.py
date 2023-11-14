import datetime
from typing import Optional
from pydantic import BaseModel


class LevelBase(BaseModel):
    name: str


class LevelCreate(LevelBase):
    pass


class LevelUpdate(LevelBase):
    name: Optional[str]


class LevelInDB(LevelBase):
    id: int
    key: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
