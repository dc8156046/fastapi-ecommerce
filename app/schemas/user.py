from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from typing import Optional, List


# Membership level
class MembershipLevel(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


# User base schema
class UserBase(BaseModel):
    email: EmailStr
    username: str


# User create schema
class UserCreate(UserBase):
    password: str


# User update schema
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    membership_level: Optional[MembershipLevel] = None
    membership_expiry: Optional[datetime] = None


# User response schema
class UserResponse(UserBase):
    id: int
    membership_level: MembershipLevel
    membership_expiry: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Password reset schema
class PasswordReset(BaseModel):
    email: EmailStr


# Password reset confirm schema
class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str


# Verify email schema
class VerifyEmail(BaseModel):
    email: EmailStr
    verification_code: str
