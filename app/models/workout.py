from sqlalchemy import Column, String, ForeignKey, event
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from .utils import generate_slug

class Workout(BaseModel):
    __tablename__ = "workouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", back_populates="workout", cascade="all, delete-orphan")

    def update_slug(self):
        """Update the slug based on the current name."""
        self.slug = generate_slug(self.name)

# Event listener to automatically update slug when name changes
@event.listens_for(Workout, 'before_insert')
@event.listens_for(Workout, 'before_update')
def update_workout_slug(mapper, connection, target):
    if hasattr(target, 'name'):
        target.update_slug() 