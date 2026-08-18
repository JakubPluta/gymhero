import datetime

from pydantic import BaseModel, ConfigDict, Field

from gymhero.schemas.exercise import ExerciseSummary


class TrainingUnitBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class TrainingUnitCreate(TrainingUnitBase):
    pass


class TrainingUnitUpdate(TrainingUnitBase):
    pass


class SetInput(BaseModel):
    # One prescribed set; order is the list position (server assigns set_number).
    reps: int | None = Field(default=None, ge=0)
    weight: float | None = Field(default=None, ge=0)


class PrescriptionUpdate(BaseModel):
    # PATCH replaces the whole prescription; an empty list clears it.
    sets: list[SetInput] = []


class PrescribedSetOut(BaseModel):
    set_number: int
    reps: int | None = None
    weight: float | None = None

    model_config = ConfigDict(from_attributes=True)


class TrainingUnitExerciseOut(BaseModel):
    exercise: ExerciseSummary
    sets: list[PrescribedSetOut] = []

    model_config = ConfigDict(from_attributes=True)


class TrainingUnitInDB(TrainingUnitBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    exercises: list[TrainingUnitExerciseOut] | None = []
    owner_id: int


class TrainingUnitOut(TrainingUnitBase):
    id: int
    exercises: list[TrainingUnitExerciseOut] | None = []
    owner_id: int
