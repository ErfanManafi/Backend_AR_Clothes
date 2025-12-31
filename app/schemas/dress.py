from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

# Base Schemas
class DressBase(BaseModel):
    title: Optional[str] = None
    gender: str = Field(..., pattern=r"^(male|female)$")

# Input Schemas
class DressCreate(DressBase):
    """شمای ورودی برای آپلود لباس (metadata)"""
    pass

class DressUpdate(DressBase):
    pass

# Output Schemas
class DressInDB(DressBase):
    """شمای خروجی لباس"""
    id: uuid.UUID
    user_id: uuid.UUID
    file_path: str 
    width: int
    height: int
    created_at: datetime

    class Config:
        from_attributes = True

# AR Session Schemas
class ARSessionCreate(BaseModel):
    """شمای ورودی برای شروع جلسه پرو مجازی"""
    dress_id: uuid.UUID

class ARSessionStatus(BaseModel):
    """شمای خروجی وضعیت جلسه پرو مجازی"""
    session_id: uuid.UUID
    status: str
    message: Optional[str] = None