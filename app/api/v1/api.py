from fastapi import APIRouter
from .endpoints import users, workouts, exercises, exercise_logs, auth, progress

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(workouts.router, prefix="/workouts", tags=["Workouts"])
api_router.include_router(exercises.router, prefix="/exercises", tags=["Exercises"])
api_router.include_router(exercise_logs.router, prefix="/exercise-logs", tags=["Exercise Logs"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress"]) 