from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from gymhero.database.base_class import Base


class BodyPart(Base):
    __tablename__ = "body_parts"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<BodyPart(id={self.id}, name={self.name})>"
