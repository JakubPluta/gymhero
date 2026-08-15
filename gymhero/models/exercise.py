from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gymhero.database.base_class import Base, TimestampMixin


class Exercise(TimestampMixin, Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    target_body_part_id: Mapped[int] = mapped_column(
        ForeignKey("body_parts.id"), index=True, nullable=False
    )
    exercise_type_id: Mapped[int] = mapped_column(
        ForeignKey("exercise_types.id"), index=True, nullable=False
    )
    level_id: Mapped[int] = mapped_column(
        ForeignKey("levels.id"), index=True, nullable=False
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )

    # Eager-loaded (selectin): the read schema ExerciseInDB embeds these as nested
    # {id, name} objects, so they must be loaded wherever an Exercise is returned
    # (list/detail/create/update, and via training_unit.exercises). selectin batches
    # them into one query per relationship — no N+1. owner stays lazy: responses
    # expose only owner_id, never the User row (PII).
    target_body_part = relationship("BodyPart", lazy="selectin")
    exercise_type = relationship("ExerciseType", lazy="selectin")
    level = relationship("Level", lazy="selectin")
    owner = relationship("User")

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, name={self.name})>"


class ExerciseType(TimestampMixin, Base):
    __tablename__ = "exercise_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<ExerciseType(id={self.id}, name={self.name})>"
