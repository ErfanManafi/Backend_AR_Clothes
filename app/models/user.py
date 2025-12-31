from sqlalchemy import Column, String, DateTime, Enum, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# فرض میکنیم که Base از app.db.base import شده است
from app.db.base import Base 

class User(Base):
    """مدل دیتابیس برای کاربران"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # رمز عبور هش شده
    gender = Column(Enum("male", "female", name="user_gender"), nullable=True)
    role = Column(Enum("admin", "user", name="user_role"), default="user", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # تعریف ارتباط یک به چند با جدول Dress
    dresses = relationship("Dress", back_populates="owner")