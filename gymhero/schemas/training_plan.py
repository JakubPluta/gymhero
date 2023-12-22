import datetime
from typing import List, Optional

from pydantic import BaseModel

from gymhero.schemas.training_unit import TrainingUnitOut


class TrainingPlanBase(BaseModel):
    name: str
    description: Optional[str] = None


class TrainingPlanCreate(TrainingPlanBase):
    pass


class TrainingPlanUpdate(TrainingPlanBase):
    pass


class TrainingPlanInDB(TrainingPlanBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    training_units: Optional[List[TrainingUnitOut]] = []
    owner_id: int


class TrainingPlanOut(TrainingPlanBase):
    id: int
    training_units: Optional[List[TrainingUnitOut]] = []
    owner_id: int
