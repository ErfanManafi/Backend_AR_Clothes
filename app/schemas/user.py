from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid

# Base Schemas
class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = Field(None, pattern=r"^(male|female)$")


# Input Schemas
class UserCreate(UserBase):
    """شمای ورودی برای ثبت نام (Sign Up)"""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """شمای ورودی برای ورود (Login)"""
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    """شمای ورودی برای ویرایش پروفایل"""
    pass


# Output Schemas
class UserInDB(UserBase):
    """شمای خروجی کاربر (شامل فیلدهای دیتابیس)"""
    id: uuid.UUID
    role: str
    created_at: datetime
    uploaded_dress_count: int = 0  # مشاهده تعداد لباس‌های آپلود شده

    class Config:
        from_attributes = True

# Security Schemas
class Token(BaseModel):
    """شمای توکن امنیتی JWT"""
    access_token: str
    token_type: str = "bearer"