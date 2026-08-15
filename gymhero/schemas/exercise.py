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


class ExerciseCreate(ExerciseBase):
    # Write side references lookups by id; the read schema embeds them as objects.
    target_body_part_id: int = Field(
        ..., gt=0, description="The id of the target body part"
    )
    exercise_type_id: int = Field(..., gt=0, description="The id of the exercise type")
    level_id: int = Field(..., gt=0, description="The id of the level")


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
    # Lookups embedded as nested {id, name} objects (read side); the raw FK ids live
    # on the write schema (ExerciseCreate). owner stays a bare id — never embed User.
    target_body_part: BodyPartOut
    exercise_type: ExerciseTypeOut
    level: LevelOut
    model_config = ConfigDict(from_attributes=True)


class ExerciseSummary(BaseModel):
    # Slim view for nested lists (a training unit's exercises): id + name + owner
    # only. No PII (email), no deep reference graph — fetch /exercises/{id} for detail.
    id: int
    name: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
