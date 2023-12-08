import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BodyPartBase(BaseModel):
    name: str


class BodyPartCreate(BodyPartBase):
    pass


class BodyPartUpdate(BodyPartBase):
    name: Optional[str] = None


class BodyPartInDB(BodyPartBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class BodyPartOut(BodyPartBase):
    id: int
    name: str
