from typing import Optional
from sqlalchemy.orm import Session
import uuid
# اگرچه در سرویس‌های دیگر تعریف شده‌اند، اما برای استفاده از Dress و uuid باید اینجا ایمپورت شوند
from app.models.user import User
from app.models.dress import Dress
from app.schemas.user import UserCreate, UserLogin, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token

class UserService:
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """کاربر را بر اساس ایمیل از دیتابیس بازیابی می کند."""
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        """کاربر جدیدی را ثبت نام می کند (Sign Up).""" # اصلاح شده
        
        # هش کردن رمز عبور
        hashed_password = get_password_hash(user_in.password)
        
        # ساخت مدل دیتابیس
        db_user = User(
            email=user_in.email,
            name=user_in.name,
            password_hash=hashed_password,
            # نقش پیش فرض: 'user'
            role="user" 
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate(self, db: Session, user_in: UserLogin) -> Optional[User]:
        """کاربر را با ایمیل و رمز عبور احراز هویت می کند (Login).""" # اصلاح شده
        user = self.get_user_by_email(db, email=user_in.email)
        
        if not user or not verify_password(user_in.password, user.password_hash):
            return None # احراز هویت ناموفق
        
        return user

    def create_token_for_user(self, user: User) -> str:
        """توکن دسترسی JWT برای کاربر ایجاد می کند.""" # اصلاح شده
        # در اینجا user.id به عنوان 'sub' (subject) استفاده می شود
        return create_access_token(subject=str(user.id))

    def update_user_profile(self, db: Session, user: User, user_in: UserUpdate) -> User:
        """پروفایل کاربر را بروزرسانی می کند (نام، جنسیت، عکس پروفایل).""" # اصلاح شده
        
        update_data = user_in.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(user, key, value)
            
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def get_user_dresses_count(self, db: Session, user_id: uuid.UUID) -> int:
        """تعداد لباس های آپلود شده توسط کاربر را برمی گرداند.""" # اصلاح شده
        return db.query(Dress).filter(Dress.user_id == user_id).count()

# ایجاد یک نمونه از سرویس برای استفاده در روترها
user_service = UserService()