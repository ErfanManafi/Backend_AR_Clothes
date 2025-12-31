import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from PIL import Image, ImageDraw

from app.core.config import settings
from app.models.dress import Dress
from app.models.user import User
from app.schemas.dress import DressCreate
from app.api.deps import CurrentUser

# اندازه استاندارد برای ریسایز خودکار [cite: 40]
TARGET_SIZE = (512, 512) 
MAX_FILE_SIZE_MB = 5 # محدودیت حجم عکس [cite: 91]

class DressService:
    
    def _validate_file(self, file: UploadFile):
        """اعتبارسنجی فرمت و حجم فایل قبل از ذخیره سازی [cite: 34, 91]"""
        
        # ۱. بررسی فرمت فایل
        allowed_formats = ["image/png", "image/jpeg", "image/jpg"]
        if file.content_type not in allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file format. Only PNG, JPEG, JPG are acceptable."
            )
            
        # ۲. بررسی حجم فایل (نیاز به خواندن کل فایل دارد که ممکن است کند باشد)
        # برای دقت بیشتر، بهتر است این کار در روتر یا Middleware انجام شود.
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
             raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the limit of {MAX_FILE_SIZE_MB} MB."
            )
            
    def _generate_alpha_mask(self, img: Image.Image) -> Image.Image:
        """
        در صورت ۳ کاناله بودن تصویر، یک Alpha Mask سفید ایجاد می‌کند. 
        این یک پیاده سازی ساده است و فرض می کند پس زمینه سفید/یکدست است.
        برای سناریوهای حرفه ای، نیاز به مدل های AI/Body Segmentation است[cite: 37, 164].
        """
        # اگر تصویر کانال آلفا ندارد (مثلاً RGB است)
        if img.mode == 'RGB':
            # یک کانال آلفای کاملاً مات (سفید) با اندازه تصویر ایجاد می کند
            alpha = Image.new('L', img.size, 255)
            img.putalpha(alpha)
            print("Alpha mask created for 3-channel image.")
            
        return img

    def _resize_image_with_alpha(self, img: Image.Image) -> Image.Image:
        """تصویر را به اندازه استاندارد ریسایز کرده و آلفا را حفظ می کند[cite: 40, 42]."""
        
        # Pillow به طور خودکار آلفا را هنگام ریسایز حفظ می کند اگر تصویر دارای آلفا باشد
        resized_img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        return resized_img

    def upload_dress(
        self, 
        db: Session, 
        user: User, 
        file: UploadFile, 
        dress_in: DressCreate
    ) -> Dress:
        """
        عملیات آپلود و پردازش تصویر را انجام می دهد.
        """
        self._validate_file(file)
        
        # ۱. ذخیره موقت فایل
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path_temp = os.path.join(settings.STORAGE_PATH, unique_filename)
        
        # ایجاد دایرکتوری در صورت عدم وجود
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)
        
        # ذخیره فایل در مسیر موقت
        try:
            with open(file_path_temp, "wb") as f:
                f.write(file.file.read())
        except Exception:
            raise HTTPException(status_code=500, detail="Could not save the uploaded file temporarily.")

        # ۲. پردازش تصویر (ریسایز و آلفا)
        try:
            img = Image.open(file_path_temp)
            
            # تشخیص و ایجاد آلفا ماسک [cite: 35]
            img = self._generate_alpha_mask(img)
            
            # سایز خودکار [cite: 38]
            img = self._resize_image_with_alpha(img)
            
            # ذخیره نسخه نهایی (ترجیحاً PNG با آلفا) [cite: 34]
            img.save(file_path_temp, "PNG") 

        except Exception as e:
            # در صورت خطا در پردازش، فایل موقت حذف شود
            if os.path.exists(file_path_temp):
                os.remove(file_path_temp)
            print(f"Image processing error: {e}")
            raise HTTPException(status_code=500, detail="Error during image processing (Resize/Alpha Mask).")

        # ۳. ذخیره رکورد در دیتابیس
        db_dress = Dress(
            user_id=user.id,
            file_path=file_path_temp, # ذخیره مسیر محلی در دیتابیس
            gender=dress_in.gender,
            title=dress_in.title if dress_in.title else file.filename,
            width=TARGET_SIZE[0],
            height=TARGET_SIZE[1]
        )
        
        db.add(db_dress)
        db.commit()
        db.refresh(db_dress)
        return db_dress

    def get_user_dresses(self, db: Session, user_id: uuid.UUID, gender: Optional[str] = None) -> list[Dress]:
        """لیست لباس های آپلود شده توسط کاربر را برمی گرداند[cite: 50]."""
        query = db.query(Dress).filter(Dress.user_id == user_id)
        if gender:
            query = query.filter(Dress.gender == gender)
        return query.order_by(Dress.created_at.desc()).all()

    def delete_dress(self, db: Session, dress: Dress):
        """حذف لباس از دیتابیس و فایل محلی[cite: 53]."""
        # ۱. حذف فایل محلی
        if os.path.exists(dress.file_path):
            os.remove(dress.file_path)
            
        # ۲. حذف از دیتابیس
        db.delete(dress)
        db.commit()
        
    def get_dress_by_id(self, db: Session, dress_id: uuid.UUID) -> Optional[Dress]:
        """بازیابی لباس بر اساس ID."""
        return db.query(Dress).filter(Dress.id == dress_id).first()

# ایجاد یک نمونه از سرویس برای استفاده در روتر
dress_service = DressService()