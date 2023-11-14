from sqlalchemy.orm import relationship

from gymhero.database.base_class import Base
from sqlalchemy import Integer, Column, String, ForeignKey, Table

from gymhero.database.utils import key_column_from

training_plan_training_unit = Table(
    "training_plan_training_unit",
    Base.metadata,
    Column("training_plan_id", Integer, ForeignKey("training_plans.id")),
    Column("training_unit_id", Integer, ForeignKey("training_units.id")),
)


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True, default=key_column_from("name"))
    name = Column(String)
    training_units = relationship("TrainingUnit", secondary=training_plan_training_unit)
