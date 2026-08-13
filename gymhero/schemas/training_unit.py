import datetime

from pydantic import BaseModel

from gymhero.schemas.exercise import ExerciseOut


class TrainingUnitBase(BaseModel):
    name: str
    description: str | None = None


class TrainingUnitCreate(TrainingUnitBase):
    pass


class TrainingUnitUpdate(TrainingUnitBase):
    pass


class TrainingUnitInDB(TrainingUnitBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: list[ExerciseOut] | None = []
    owner_id: int


class TrainingUnitOut(TrainingUnitBase):
    id: int
    exercises: list[ExerciseOut] | None = []
    owner_id: int
