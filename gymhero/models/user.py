from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gymhero.database.base_class import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool | None] = mapped_column(Boolean, default=False)

    training_plans = relationship("TrainingPlan", back_populates="owner")
    training_units = relationship("TrainingUnit", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User(full_name={self.full_name}, email={self.email})>"
