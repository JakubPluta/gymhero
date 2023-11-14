from gymhero.database.base_class import Base
from sqlalchemy import Integer, String, DateTime, Column
from sqlalchemy import func
from gymhero.database.utils import key_column_from


class BodyPart(Base):
    __tablename__ = "body_parts"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True, default=key_column_from("name"))
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<BodyPart(id={self.id}, key={self.key}, name={self.name})>"
