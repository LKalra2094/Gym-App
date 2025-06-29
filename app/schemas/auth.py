from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from uuid import UUID


# --- 🔒 Reusable password strength validator ---
def validate_password_strength(value: str) -> str:
    if not any(c.isupper() for c in value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in value):
        raise ValueError("Password must contain at least one number")
    return value


# --- 🔐 Auth Token Models ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: UUID | None = None


# --- 👤 Login ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- 🆕 Registration ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @field_validator("password")
    def password_strength(cls, v):
        return validate_password_strength(v)

    @model_validator(mode='after')
    def passwords_match(self):
        pw = self.password
        cpw = self.confirm_password
        if pw != cpw:
            raise ValueError("Passwords do not match")
        return self


# --- 🔄 Change Password ---
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    def password_strength(cls, v):
        return validate_password_strength(v)


# --- 🔁 Password Reset Request ---
class PasswordResetRequest(BaseModel):
    email: EmailStr


# --- 🔁 Password Reset ---
class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @field_validator("new_password")
    def password_strength(cls, v):
        return validate_password_strength(v)

    @model_validator(mode='after')
    def passwords_match(self):
        pw = self.new_password
        cpw = self.confirm_password
        if pw != cpw:
            raise ValueError("Passwords do not match")
        return self


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


# --- ✅ Email Verification ---
class EmailVerification(BaseModel):
    token: str
