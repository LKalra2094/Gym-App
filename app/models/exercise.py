from __future__ import annotations
import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.exercise_log import ExerciseLog


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    workout_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("workouts.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey("users.id"))

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    logs: Mapped[list["ExerciseLog"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Exercise(id={self.id}, name={self.name})>"
