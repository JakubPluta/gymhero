import datetime
from typing import List, Optional

from pydantic import BaseModel

from gymhero.schemas.training_unit import TrainingUnitInDB


class TrainingPlanBase(BaseModel):
    name: str
    description: str


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlanUpdate(TrainingPlanBase):
    pass


class TrainingPlanInDB(TrainingPlanBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    training_units: Optional[List[TrainingUnitInDB]] = []
    owner_id: int


class TrainingPlansInDB(BaseModel):
    results: List[TrainingUnitInDB]
