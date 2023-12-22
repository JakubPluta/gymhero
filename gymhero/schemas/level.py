import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LevelBase(BaseModel):
    name: str


class LevelCreate(LevelBase):
    pass


class LevelUpdate(LevelBase):
    name: Optional[str] = None


class LevelInDB(LevelBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class LevelOut(LevelBase):
    id: int
