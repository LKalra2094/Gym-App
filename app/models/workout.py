from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.exercise import Exercise


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="workouts")

    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="workout", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Workout(id={self.id}, name={self.name})>"