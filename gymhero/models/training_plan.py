from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gymhero.database.base_class import Base

training_plan_training_unit = Table(
    "training_plan_training_unit",
    Base.metadata,
    Column("training_plan_id", Integer, ForeignKey("training_plans.id")),
    Column("training_unit_id", Integer, ForeignKey("training_units.id")),
)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    __table_args__ = (
        # this can be db.PrimaryKeyConstraint if you want it to be a primary key
        UniqueConstraint("name", "owner_id"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="training_plans")
    training_units = relationship("TrainingUnit", secondary=training_plan_training_unit)

    def __repr__(self):
        return f"TrainingPlan(id={self.id}, name={self.name})"
