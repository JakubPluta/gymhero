import datetime
from typing import Optional, List
from pydantic import BaseModel
from gymhero.schemas.exercise import ExerciseInDB


class TrainingUnitBase(BaseModel):
    name: str
    description: str


class TrainingUnitCreate(TrainingUnitBase):
    pass


class TrainingUnitUpdate(TrainingUnitBase):
    pass


class TrainingUnitInDB(TrainingUnitBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: Optional[List[ExerciseInDB]] = []
    owner_id: int


class TrainingUnitsInDB(BaseModel):
    results: List[TrainingUnitInDB]
