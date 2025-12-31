import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from PIL import Image

from app.core.config import settings
from app.models.dress import Dress
from app.models.user import User
from app.schemas.dress import DressCreate

TARGET_SIZE = (512, 512) 
MAX_FILE_SIZE_MB = 5 

class DressService:
    
    def _validate_file(self, file: UploadFile):
        """اعتبارسنجی فرمت و حجم فایل"""
        allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
        if file.content_type not in allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="فرمت فایل نامعتبر است. فقط PNG و JPG مجاز هستند."
            )
        
        # بررسی حجم فایل بدون خواندن کل آن در حافظه (اگر سرور ساپورت کند)
        if file.size and file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
             raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"حجم فایل نباید بیشتر از {MAX_FILE_SIZE_MB} مگابایت باشد."
            )

    def upload_dress(
        self, 
        db: Session, 
        user: User, 
        file: UploadFile, 
        dress_in: DressCreate
    ) -> Dress:
        self._validate_file(file)
        
        # ۱. ساخت نام منحصر به فرد (فقط UUID + پسوند اصلی)
        extension = os.path.splitext(file.filename)[1].lower()
        if not extension: extension = ".png" # پیش‌فرض
        
        unique_filename = f"{uuid.uuid4()}{extension}"
        # استفاده از مسیر نسبی برای ذخیره در دیتابیس (بهتر برای جابجایی پروژه)
        relative_path = os.path.join(settings.STORAGE_PATH, unique_filename)
        absolute_path = os.path.abspath(relative_path)
        
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        
        # ۲. ذخیره فایل به صورت Chunk (بهینه برای حافظه RAM)
        try:
            with open(absolute_path, "wb") as f:
                # خواندن فایل در قطعات ۱۰۲۴ بایتی
                while content := file.file.read(1024 * 1024):
                    f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"خطا در ذخیره فایل: {e}")

        # ۳. پردازش تصویر (Resize و تبدیل به PNG برای حفظ Alpha)
        try:
            with Image.open(absolute_path) as img:
                # ایجاد کانال آلفا اگر وجود ندارد
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # ریسایز با کیفیت بالا
                img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # ذخیره نهایی (جایگزین کردن فایل اصلی با نسخه بهینه شده PNG)
                final_filename = unique_filename.replace(extension, ".png")
                final_relative_path = os.path.join(settings.STORAGE_PATH, final_filename)
                final_absolute_path = os.path.abspath(final_relative_path)
                
                img.save(final_absolute_path, "PNG")
                
                # اگر پسوند عوض شده، فایل موقت قبلی حذف شود
                if absolute_path != final_absolute_path:
                    os.remove(absolute_path)
        except Exception as e:
            if os.path.exists(absolute_path): os.remove(absolute_path)
            raise HTTPException(status_code=500, detail="خطا در پردازش تصویر.")

        # ۴. ذخیره در دیتابیس
        db_dress = Dress(
            user_id=user.id,
            file_path=final_relative_path, # مسیر نسبی ذخیره می‌شود
            gender=dress_in.gender,
            title=dress_in.title or file.filename,
            width=TARGET_SIZE[0],
            height=TARGET_SIZE[1]
        )
        
        db.add(db_dress)
        db.commit()
        db.refresh(db_dress)
        return db_dress

    # بقیه متدها (get, delete, ...) به قوت خود باقی هستند
    def get_user_dresses(self, db: Session, user_id: uuid.UUID, gender: Optional[str] = None) -> list[Dress]:
        query = db.query(Dress).filter(Dress.user_id == user_id)
        if gender:
            query = query.filter(Dress.gender == gender)
        return query.order_by(Dress.created_at.desc()).all()

    def get_dress_by_id(self, db: Session, dress_id: uuid.UUID) -> Optional[Dress]:
        return db.query(Dress).filter(Dress.id == dress_id).first()

dress_service = DressService()