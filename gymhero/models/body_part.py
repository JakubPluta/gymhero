from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gymhero.database.base_class import Base, TimestampMixin


class BodyPart(TimestampMixin, Base):
    __tablename__ = "body_parts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<BodyPart(id={self.id}, name={self.name})>"
