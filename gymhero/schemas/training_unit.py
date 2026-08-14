import datetime

from pydantic import BaseModel, Field

from gymhero.schemas.exercise import ExerciseOut


class TrainingUnitBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)


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
