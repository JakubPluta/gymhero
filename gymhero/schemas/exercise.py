import datetime
from typing import Optional

from pydantic import BaseModel


class ExerciseBase(BaseModel):
    name: str
    description: Optional[str]
    target_body_part_id: int
    exercise_type_id: int
    level_id: int


class ExerciseCreate(ExerciseBase):
    ...


class ExerciseUpdate(ExerciseBase):
    name: Optional[str]
    description: Optional[str]
    target_body_part_id: Optional[int]
    exercise_type_id: Optional[int]
    level_id: Optional[int]


class ExerciseInDB(ExerciseBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: int

    class Config:
        orm_mode = True
