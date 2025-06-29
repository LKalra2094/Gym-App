from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import UserRole, Gender


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    birthday: Mapped[datetime.date]
    gender: Mapped[Gender]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    is_verified: Mapped[bool] = mapped_column(default=False)
    verification_token: Mapped[str | None]
    reset_token: Mapped[str | None]
    reset_token_expires: Mapped[datetime.datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True)
    )

    workouts: Mapped[list["Workout"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def age(self) -> int:
        today = datetime.date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
