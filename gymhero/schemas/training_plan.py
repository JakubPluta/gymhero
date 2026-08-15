import datetime

from pydantic import BaseModel, Field

from gymhero.schemas.training_unit import TrainingUnitOut


class TrainingPlanBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlanUpdate(TrainingPlanBase):
    pass


class TrainingPlanInDB(TrainingPlanBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    training_units: list[TrainingUnitOut] | None = []
    owner_id: int


class TrainingPlanOut(TrainingPlanBase):
    id: int
    training_units: list[TrainingUnitOut] | None = []
    owner_id: int
