from gymhero.database.base_class import Base
from sqlalchemy import Integer, String, DateTime, Column
from sqlalchemy import func
from gymhero.database.utils import key_column_from


class Level(Base):
    __tablename__ = "levels"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Level(id={self.id}, name={self.name})>"
