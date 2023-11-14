from gymhero.database.base_class import Base
from sqlalchemy import Integer, String, DateTime, ForeignKey, Unicode, Column
from sqlalchemy.orm import relationship
from sqlalchemy import func
from gymhero.database.utils import key_column_from


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True, default=key_column_from("name"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_body_part_id = Column(Integer, ForeignKey("body_parts.id"))
    exercise_type_id = Column(Integer, ForeignKey("exercise_types.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    target_body_part = relationship("BodyPart")
    exercise_type = relationship("ExerciseType")
    level = relationship("Level")

    def __repr__(self):
        return f"<Exercise(id={self.id}, key={self.key}, name={self.name})>"


class ExerciseType(Base):
    __tablename__ = "exercise_types"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True, default=key_column_from("name"))
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<ExerciseType(id={self.id}, key={self.key}, name={self.name})>"
