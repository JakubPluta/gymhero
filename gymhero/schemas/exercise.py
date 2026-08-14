import datetime

from pydantic import BaseModel, ConfigDict, Field

from gymhero.schemas.body_part import BodyPartOut
from gymhero.schemas.exercise_type import ExerciseTypeOut
from gymhero.schemas.level import LevelOut


class ExerciseBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(
        default=None, max_length=2000, title="The description of the exercise"
    )

    target_body_part_id: int = Field(
        ..., gt=0, description="The id of the target body part"
    )
    exercise_type_id: int = Field(..., gt=0, description="The id of the exercise type")
    level_id: int = Field(..., gt=0, description="The id of the level")


class ExerciseCreate(ExerciseBase): ...


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    target_body_part_id: int | None = None
    exercise_type_id: int | None = None
    level_id: int | None = None


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
    description: str | None = None
    owner_id: int  # expose the owner id only — never the owner's email (PII)
    target_body_part: BodyPartOut | None
    exercise_type: ExerciseTypeOut | None
    level: LevelOut | None

    model_config = ConfigDict(from_attributes=True)
