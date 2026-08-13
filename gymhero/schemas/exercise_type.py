import datetime

from pydantic import BaseModel, ConfigDict


class ExerciseTypeBase(BaseModel):
    name: str


class ExerciseTypeCreate(ExerciseTypeBase):
    pass


class ExerciseTypeUpdate(BaseModel):
    name: str | None = None


class ExerciseTypeInDB(ExerciseTypeBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)


class ExerciseTypeOut(ExerciseTypeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
