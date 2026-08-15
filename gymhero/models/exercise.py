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

    # Not eager-loaded: list/detail endpoints use the *_id columns, and nested
    # views (ExerciseSummary) don't touch these. Add selectinload() explicitly if
    # a future endpoint needs the related rows.
    target_body_part = relationship("BodyPart")
    exercise_type = relationship("ExerciseType")
    level = relationship("Level")
    owner = relationship("User")

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, name={self.name})>"


class ExerciseType(TimestampMixin, Base):
    __tablename__ = "exercise_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<ExerciseType(id={self.id}, name={self.name})>"
