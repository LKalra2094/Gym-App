from __future__ import annotations
import uuid
from typing import Optional

from sqlalchemy import Float, Integer, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base
from .enums import WeightUnit

class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exercises.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id")
    )
    date: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    weight: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    weight_unit: Mapped[WeightUnit] = mapped_column(
        Enum(
            WeightUnit,
            values_callable=lambda x: [e.value for e in x],
            native_enum=False
        ),
        nullable=False
    )
    reps: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    sets: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    exercise: Mapped["Exercise"] = relationship(
        "Exercise", back_populates="logs"
    )
