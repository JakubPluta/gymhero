import datetime
from typing import Optional

from pydantic import BaseModel


class ExerciseTypeBase(BaseModel):
    name: str


class ExerciseTypeCreate(ExerciseTypeBase):
    pass


class ExerciseTypeUpdate(ExerciseTypeBase):
    name: Optional[str]


class ExerciseTypeInDB(ExerciseTypeBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
