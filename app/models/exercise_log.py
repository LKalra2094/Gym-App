from sqlalchemy import Column, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from .enums import WeightUnit

class ExerciseLog(BaseModel):
    __tablename__ = "exercise_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    weight = Column(Float)
    weight_unit = Column(Enum(WeightUnit))
    reps = Column(Integer)
    sets = Column(Integer)

    exercise = relationship("Exercise", back_populates="logs")
    user = relationship("User", back_populates="exercise_logs") 