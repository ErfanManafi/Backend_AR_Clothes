import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import uuid

# --- رفع مشکل Python Path: تنظیم Path قبل از تمام import ها ---
import sys
import os

# اضافه کردن مسیر ریشه پروژه (پوشه erfan) به Python Path
# این خط باید قبل از تمام import هایی که از 'app' استفاده می کنند، قرار گیرد.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -------------------------------------------------------------------

# حالا import ها باید کار کنند
from main import app
from app.db.base import Base
from app.models.user import User
from app.models.dress import Dress 
from app.core.security import get_password_hash 
from app.api.deps import get_db

# ------------------- تنظیمات دیتابیس تست (SQLite) -------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" 

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """ایجاد و حذف جداول دیتابیس برای هر جلسه تست."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """ایجاد یک Session دیتابیس تمیز و Rollback شده برای هر تست."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield session

    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """ایجاد کلاینت تست FastAPI."""
    with TestClient(app) as c:
        yield c

# ------------------- Fixture های احراز هویت -------------------

@pytest.fixture
def test_admin_user(db_session: Session) -> User:
    """ساخت یک کاربر ادمین برای تست."""
    user = User(
        id=uuid.uuid4(),
        email="admin@test.com",
        password_hash=get_password_hash("adminpass"),
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_auth_headers(test_admin_user: User) -> dict:
    """ایجاد هدرهای احراز هویت معتبر برای کاربر ادمین."""
    from app.core.security import create_access_token
    token = create_access_token(subject=str(test_admin_user.id))
    return {"Authorization": f"Bearer {token}"}