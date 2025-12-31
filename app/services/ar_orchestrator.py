import subprocess
import os
import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.dress import Dress
from app.schemas.dress import ARSessionStatus

class AROrchestrator:
    """
    مسئول هماهنگی اجرای موتور پرو مجازی (کد پایتون گیت هاب)
    """
    
    def start_ar_session(self, db: Session, dress: Dress) -> ARSessionStatus:
        """
        اجرای اسکریپت پایتون AR Engine به عنوان یک فرآیند جداگانه.
        """
        
        # ۱. اعتبارسنجی اسکریپت
        if not os.path.exists(settings.AR_ENGINE_SCRIPT_PATH):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AR Engine script not found at path: {settings.AR_ENGINE_SCRIPT_PATH}. Please check .env settings."
            )
        
        # ۲. تعریف آرگومان ها برای اسکریپت AR
        # فرض می کنیم اسکریپت AR آرگومان هایی را برای مسیر فایل لباس و جنسیت دریافت می کند.
        # (مانند: python main.py --dress_path <path> --gender <gender>)
        command = [
            "python", # یا "python3" بسته به محیط
            settings.AR_ENGINE_SCRIPT_PATH,
            "--dress_path", dress.file_path, # ارسال مسیر محلی فایل به اسکریپت AR 
            "--gender", dress.gender,
            "--session_id", str(uuid.uuid4()) # یک شناسه برای ردیابی (اگر لازم باشد)
        ]

        try:
            # اجرای اسکریپت به صورت non-blocking (بدون منتظر ماندن)
            # این اجازه می دهد که FastAPI بلافاصله پاسخ را برگرداند در حالی که پنجره AR باز می شود.
            # استفاده از Popen اجازه می دهد فرآیند AR در پس زمینه اجرا شود.
            # توجه: در یک محیط تولید واقعی، ممکن است نیاز به فرآیند مدیریت پیچیده تر باشد.
            
            # Subprocess.Popen یک فرآیند جدید را شروع می کند
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                # برای ویندوز ممکن است نیاز به creationflags خاص باشد
                # creationflags=subprocess.CREATE_NEW_CONSOLE 
            )
            
            # در اینجا فرض می کنیم که اگر دستور با موفقیت اجرا شد، جلسه شروع شده است.
            session_id = uuid.uuid4()
            
            # ذخیره اطلاعات session (اگر نیاز به ردیابی فرآیند باشد، باید در دیتابیس ذخیره شود)
            
            print(f"AR Engine started for Dress ID: {dress.id} with PID: {process.pid}")

            return ARSessionStatus(
                session_id=session_id,
                status="started",
                message=f"AR Engine process started with PID {process.pid}. A full-screen window should open shortly."
            )
            
        except FileNotFoundError:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Python executable not found. Check if 'python' is in your PATH."
            )
        except Exception as e:
            print(f"Error starting AR Engine: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start the Virtual Try-On Engine. Error: {e}"
            )

# ایجاد یک نمونه از سرویس
ar_orchestrator = AROrchestrator()