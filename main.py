from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

# ------------------- Import روترها -------------------
from app.api.v1.routers import users, dresses, ar_session 

# ------------------- Import مدل های دیتابیس -------------------
from app.db.base import Base 
from app.db.session import engine

# ------------------- توابع راه اندازی -------------------

def create_tables():
    """ایجاد جداول دیتابیس بر اساس مدل های SQLAlchemy"""
    from app.models import user, dress
    Base.metadata.create_all(bind=engine)

def get_application():
    """ایجاد نمونه برنامه FastAPI و تنظیمات"""
    
    # ۱. ایجاد جداول دیتابیس (فقط در شروع توسعه)
    try:
        create_tables() 
    except Exception as e:
        print(f"Warning: Could not create database tables. Ensure PostgreSQL is running. Error: {e}")
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        version="1.0.0"
    )
    
    # ۲. افزودن روترها با پیشوند صحیح
    # اصلاح: اضافه کردن /users و ... به انتهای prefix
    application.include_router(users.router, tags=["Users"], prefix=f"{settings.API_V1_STR}/users")
    application.include_router(dresses.router, tags=["Dresses"], prefix=f"{settings.API_V1_STR}/dresses")
    application.include_router(ar_session.router, tags=["AR Session"], prefix=f"{settings.API_V1_STR}/ar-session")

    # ۳. Mount کردن پوشه Storage
    application.mount(
        "/storage/dresses", 
        StaticFiles(directory=settings.STORAGE_PATH),
        name="dresses-storage"
    )
    
    return application

app = get_application()