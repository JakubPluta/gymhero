import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from gymhero.schemas.body_part import BodyPartOut
from gymhero.schemas.exercise_type import ExerciseTypeOut
from gymhero.schemas.level import LevelOut
from gymhero.schemas.user import UserOut


class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = Field(
        default=None, title="The description of the exercise"
    )

    target_body_part_id: int = Field(
        ..., gt=0, description="The id of the target body part"
    )
    exercise_type_id: int = Field(..., gt=0, description="The id of the exercise type")
    level_id: int = Field(..., gt=0, description="The id of the level")


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


# TODO: https://stackoverflow.com/questions/68799438/how-to-return-only-one-column-from-database-in-pydantic-model-as-a-list


class ExerciseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner: Optional[UserOut]
    target_body_part: Optional[BodyPartOut]
    exercise_type: Optional[ExerciseTypeOut]
    level: Optional[LevelOut]

    model_config = ConfigDict(from_attributes=True)
