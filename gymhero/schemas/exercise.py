import datetime
from typing import Optional

from pydantic import ConfigDict, BaseModel


class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_body_part_id: int
    exercise_type_id: int
    level_id: int


class ExerciseCreate(ExerciseBase):
    ...


class ExerciseUpdate(ExerciseBase):
    name: Optional[str] = None
    description: Optional[str] = None
    target_body_part_id: Optional[int] = None
    exercise_type_id: Optional[int] = None
    level_id: Optional[int] = None


class ExerciseInDB(ExerciseBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: int
    model_config = ConfigDict(from_attributes=True)
