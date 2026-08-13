from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gymhero.database.base_class import Base, TimestampMixin


class Level(TimestampMixin, Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Level(id={self.id}, name={self.name})>"
