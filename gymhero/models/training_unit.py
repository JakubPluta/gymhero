from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gymhero.database.base_class import Base, TimestampMixin

training_unit_exercise = Table(
    "training_unit_exercise",
    Base.metadata,
    Column(
        "training_unit_id",
        ForeignKey("training_units.id"),
        primary_key=True,
    ),
    Column(
        "exercise_id",
        ForeignKey("exercises.id"),
        primary_key=True,
    ),
)


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
    exercises = relationship(
        "Exercise", secondary=training_unit_exercise, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"TrainingUnit(id={self.id}, name={self.name})"
