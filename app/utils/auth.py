from fastapi import Depends, HTTPException, status
from app.models.user import User
from uuid import UUID
from app.core.security import get_current_user

def require_admin(current_user: User = Depends(get_current_user)):
    """Check if the current user is an admin."""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def check_user_access(current_user: User, target_user_id: UUID):
    """Check if the current user has access to the target user's data."""
    if not current_user.can_access_user_data(target_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource."
        ) 