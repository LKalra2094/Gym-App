from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
import uuid
from datetime import date
from app.models.enums import UserRole, WeightUnit, Gender

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    birthday: date
    gender: Gender
    role: UserRole = UserRole.USER
    is_verified: bool = False

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    birthday: date | None = None
    gender: Gender | None = None
    role: UserRole | None = None
    is_verified: bool | None = None

class UserResponse(UserBase):
    id: uuid.UUID
    age: int

    model_config = ConfigDict(from_attributes=True)