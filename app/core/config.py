from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Virtual Try-On API"
    API_V1_STR: str = "/api/v1"
    
    # مقادیر پیش‌فرض بگذارید تا Pydantic خطا ندهد
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "db"
    
    # ------------------- تغییر مهم -------------------
    # به جای آدرس پستگرس، آدرس فایل SQLite را برگردانید
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return "sqlite:///./sql_app.db"

    SECRET_KEY: str = "test_secret_key_123456789" # یک مقدار موقت
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    STORAGE_PATH: str = "storage/dresses"
    
    # مسیر اسکریپت AR را به یک فایل ساختگی تغییر دهید (در مرحله بعد می‌سازیم)
    AR_ENGINE_SCRIPT_PATH: str = "mock_ar.py"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()