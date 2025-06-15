from sqlalchemy import Column, String, ForeignKey, event
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from .utils import generate_slug

class Exercise(BaseModel):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    workout_id = Column(UUID(as_uuid=True), ForeignKey("workouts.id"))

    workout = relationship("Workout", back_populates="exercises")
    logs = relationship("ExerciseLog", back_populates="exercise", cascade="all, delete-orphan")

    def update_slug(self):
        """Update the slug based on the current name."""
        self.slug = generate_slug(self.name)

# Event listener to automatically update slug when name changes
@event.listens_for(Exercise, 'before_insert')
@event.listens_for(Exercise, 'before_update')
def update_exercise_slug(mapper, connection, target):
    if hasattr(target, 'name'):
        target.update_slug() 