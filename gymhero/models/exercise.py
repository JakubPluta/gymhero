from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gymhero.database.base_class import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    target_body_part_id = Column(Integer, ForeignKey("body_parts.id"))
    exercise_type_id = Column(Integer, ForeignKey("exercise_types.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    target_body_part = relationship("BodyPart")
    exercise_type = relationship("ExerciseType")
    level = relationship("Level")
    owner = relationship("User")

    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name})>"


class ExerciseType(Base):
    __tablename__ = "exercise_types"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ExerciseType(id={self.id}, name={self.name})>"
