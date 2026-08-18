from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gymhero.database.base_class import Base, TimestampMixin


class PrescribedSet(Base):
    # One prescribed set within a unit's exercise (reps x weight), ordered by set_number.
    __tablename__ = "prescribed_set"

    id: Mapped[int] = mapped_column(primary_key=True)
    training_unit_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("training_unit_exercise.id"), index=True, nullable=False
    )
    set_number: Mapped[int] = mapped_column(nullable=False)
    reps: Mapped[int | None] = mapped_column(nullable=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"PrescribedSet(id={self.id}, set_number={self.set_number})"


class TrainingUnitExercise(Base):
    # Association object between a unit and an exercise; owns the ordered
    # prescription — a list of PrescribedSet rows (surrogate id so sets can FK to it).
    __tablename__ = "training_unit_exercise"

    __table_args__ = (UniqueConstraint("training_unit_id", "exercise_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    training_unit_id: Mapped[int] = mapped_column(
        ForeignKey("training_units.id"), nullable=False
    )
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"), nullable=False)

    exercise = relationship("Exercise", lazy="selectin")
    sets: Mapped[list[PrescribedSet]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="PrescribedSet.set_number",
    )

    def __repr__(self) -> str:
        return f"TrainingUnitExercise(id={self.id}, exercise_id={self.exercise_id})"


class TrainingUnit(TimestampMixin, Base):
    __tablename__ = "training_units"

    __table_args__ = (UniqueConstraint("name", "owner_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )

    owner = relationship("User")
    # Link rows, not Exercise objects — each carries its own ordered prescription.
    exercises: Mapped[list[TrainingUnitExercise]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"TrainingUnit(id={self.id}, name={self.name})"
