import datetime
from typing import List, Optional

from pydantic import BaseModel

from gymhero.schemas.exercise import ExerciseOut


class TrainingUnitBase(BaseModel):
    name: str
    description: Optional[str] = None


class TrainingUnitCreate(TrainingUnitBase):
    pass


class TrainingUnitUpdate(TrainingUnitBase):
    pass


class TrainingUnitInDB(TrainingUnitBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: Optional[List[ExerciseOut]] = []
    owner_id: int


class TrainingUnitOut(TrainingUnitBase):
    id: int
    exercises: Optional[List[ExerciseOut]] = []
    owner_id: int
