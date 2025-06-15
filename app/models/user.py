from sqlalchemy import Column, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from .enums import UserRole, WeightUnit

class User(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    preferred_weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)

    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    exercise_logs = relationship("ExerciseLog", back_populates="user")

    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN

    def can_access_user_data(self, target_user_id: uuid.UUID) -> bool:
        """Check if user has permission to access another user's data."""
        # Admins can access any user's data
        if self.is_admin():
            return True
        # Regular users can only access their own data
        return self.id == target_user_id 