from sqlalchemy import Column, ForeignKey, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gymhero.database.base_class import Base, TimestampMixin

training_plan_training_unit = Table(
    "training_plan_training_unit",
    Base.metadata,
    Column(
        "training_plan_id",
        ForeignKey("training_plans.id"),
        primary_key=True,
    ),
    Column(
        "training_unit_id",
        ForeignKey("training_units.id"),
        primary_key=True,
    ),
)


class TrainingPlan(TimestampMixin, Base):
    __tablename__ = "training_plans"

    __table_args__ = (UniqueConstraint("name", "owner_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), index=True, nullable=False
    )

    owner = relationship("User", back_populates="training_plans")
    training_units = relationship(
        "TrainingUnit", secondary=training_plan_training_unit, lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"TrainingPlan(id={self.id}, name={self.name})"
