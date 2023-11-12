import datetime

from pydantic import BaseModel, Field
from typing import Optional, List, Any

from pydantic import validator, BaseModel




class LevelBase(BaseModel):
    name: str
    # key: str = ''
    #
    # @validator("key", always=True)
    # def populate_key(cls, v, values):
    #     return str(values["name"]).replace(" ", "_").lower()


class LevelCreate(LevelBase):
    pass


class LevelInDB(LevelBase):
    id: int
    key: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

