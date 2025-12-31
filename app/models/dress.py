from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# فرض میکنیم که Base از app.db.base import شده است
from app.db.base import Base

class Dress(Base):
    """مدل دیتابیس برای لباس های آپلود شده"""
    __tablename__ = "dresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # کلید خارجی به کاربر
    file_path = Column(String, nullable=False) # مسیر ذخیره سازی محلی تصویر
    gender = Column(Enum("male", "female", name="dress_gender"), nullable=False) # دسته بندی جنسیتی (مردانه/زنانه)
    title = Column(String, index=True, nullable=True) # نام لباس
    
    # ابعاد تصویر بعد از Auto-Resize
    width = Column(Integer, nullable=False, default=512) 
    height = Column(Integer, nullable=False, default=512) 

    created_at = Column(DateTime, default=datetime.utcnow)

    # ارتباط با جدول User (مالک لباس)
    owner = relationship("User", back_populates="dresses")