from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseSchema):
    email: EmailStr


class UserCreate(BaseSchema):
    email: EmailStr
    password_hash: str


class UserRegister(BaseSchema):
    email: EmailStr
    plain_password: str

    @field_validator("plain_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None


class User(BaseSchema):
    id: UUID
    created_at: datetime


class UserProfileBase(BaseSchema):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


class UserProfileCreate(BaseSchema):
    pass


class UserProfileUpdate(BaseSchema):
    pass


class UserProfile(BaseSchema):
    user_id: UUID


class UserWithProfile(BaseSchema):
    user: User
    profile: Optional[UserProfile] = None


class PasswordChange(BaseSchema):
    old_password: str
    new_password: str


class PortfolioSummary(BaseSchema):
    id: UUID
    name: str
    created_at: datetime
    assets_count: int
