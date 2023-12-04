from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from gymhero.database.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    training_plans = relationship("TrainingPlan", back_populates="owner")
    training_units = relationship("TrainingUnit", back_populates="owner")

    def __repr__(self):
        return f"<User(full_name={self.full_name}, email={self.email})>"
