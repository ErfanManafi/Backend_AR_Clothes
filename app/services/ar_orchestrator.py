import subprocess
import os
import uuid
import sys
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.dress import Dress
from app.schemas.dress import ARSessionStatus

class AROrchestrator:
    """
    مسئول هماهنگی و اجرای موتور پرو مجازی (AR Engine) به عنوان یک فرآیند جداگانه.
    """
    
    def start_ar_session(self, db: Session, dress: Dress) -> ARSessionStatus:
        """
        اجرای اسکریپت پایتون AR Engine و ارسال پارامترهای لازم.
        """
        
        # ۱. اعتبارسنجی وجود اسکریپت در مسیر تعیین شده
        # اگر در .env فقط اسم فایل (mock_ar.py) را دادید، این کد آن را پیدا می‌کند
        script_path = os.path.abspath(settings.AR_ENGINE_SCRIPT_PATH)
        
        if not os.path.exists(script_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"فایل موتور AR در مسیر زیر یافت نشد: {script_path}. لطفا تنظیمات .env را چک کنید."
            )
        
        # ۲. تعریف آرگومان‌ها برای ارسال به اسکریپت AR
        # ما مسیر فایل لباس، جنسیت و یک ID یکتا برای این جلسه (Session) ارسال می‌کنیم
        current_session_id = str(uuid.uuid4())
        
        command = [
            sys.executable,          # استفاده از مفسر پایتون فعلی (بسیار مهم برای venv)
            script_path,             # مسیر اسکریپت (مثلاً mock_ar.py)
            "--dress_path", dress.file_path, 
            "--gender", dress.gender,
            "--session_id", current_session_id
        ]

        try:
            # ۳. اجرای اسکریپت به صورت Non-blocking (در پس‌زمینه)
            # این کار باعث می‌شود API منتظر تمام شدن کار AR نماند و سریع پاسخ دهد
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # چاپ لاگ در ترمینال سرور برای مانیتورینگ
            print(f"🚀 AR Engine started | Dress ID: {dress.id} | PID: {process.pid}")

            return ARSessionStatus(
                session_id=uuid.UUID(current_session_id),
                status="started",
                message=f"موتور پرو مجازی با موفقیت اجرا شد (PID: {process.pid}). خروجی را در ترمینال چک کنید."
            )
            
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="مفسر پایتون یافت نشد. مطمئن شوید Python در PATH سیستم قرار دارد."
            )
        except Exception as e:
            print(f"❌ Error starting AR Engine: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"خطا در اجرای موتور پرو مجازی: {str(e)}"
            )

# ایجاد یک نمونه واحد از سرویس برای استفاده در کل پروژه
ar_orchestrator = AROrchestrator()