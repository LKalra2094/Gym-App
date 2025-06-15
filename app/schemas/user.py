from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from .weight_unit import WeightUnit
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    preferred_weight_unit: WeightUnit = WeightUnit.KG

class UserCreate(UserBase):
    password: constr(min_length=8)

    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    preferred_weight_unit: Optional[WeightUnit] = None
    password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: UUID
    is_verified: bool
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: constr(min_length=8)

class PasswordChange(BaseModel):
    current_password: str
    new_password: constr(min_length=8)

class User(UserBase):
    id: UUID
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 