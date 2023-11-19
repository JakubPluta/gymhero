from gymhero.database.base_class import Base
from sqlalchemy import Integer, String, DateTime, ForeignKey, Unicode, Column
from sqlalchemy.orm import relationship
from sqlalchemy import func


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
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
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ExerciseType(id={self.id}, name={self.name})>"
