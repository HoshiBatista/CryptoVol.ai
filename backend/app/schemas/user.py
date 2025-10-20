from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password_hash: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None


class User(UserBase):
    id: str
    created_at: str

    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    settings: Optional[dict] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    user_id: str

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True
