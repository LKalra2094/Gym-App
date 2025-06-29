from fastapi import APIRouter
from app.api.v1.endpoints import (
    users,
    auth,
    workouts,
    exercises,
    exercise_logs,
    progress
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["workouts"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["exercises"])
api_router.include_router(exercise_logs.router, prefix="/exercise-logs", tags=["exercise-logs"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])

@api_router.get("/health", status_code=200, tags=["health"])
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}
