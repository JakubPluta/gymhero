from sqlalchemy.orm import relationship

from gymhero.database.base_class import Base
from sqlalchemy import Integer, Column, String, ForeignKey, Table

training_plan_training_unit = Table(
    "training_plan_training_unit",
    Base.metadata,
    Column("training_plan_id", Integer, ForeignKey("training_plans.id")),
    Column("training_unit_id", Integer, ForeignKey("training_units.id")),
)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    numer_of_training_units = Column(Integer)
    training_units = relationship("TrainingUnit", secondary=training_plan_training_unit)
