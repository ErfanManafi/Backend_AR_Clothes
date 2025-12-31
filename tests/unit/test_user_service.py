import pytest
from sqlalchemy.orm import Session

from app.services.user_service import user_service
from app.schemas.user import UserCreate, UserLogin

def test_create_user(db_session: Session):
    """تست ثبت نام کاربر جدید."""
    user_in = UserCreate(email="test@example.com", password="securepassword123")
    user = user_service.create_user(db_session, user_in)
    
    assert user.email == "test@example.com"
    assert user.role == "user"
    assert hasattr(user, "password_hash")

def test_authenticate_success(db_session: Session):
    """تست ورود موفقیت آمیز."""
    user_in = UserCreate(email="auth@example.com", password="testpass")
    user_service.create_user(db_session, user_in)
    
    user_login = UserLogin(email="auth@example.com", password="testpass")
    authenticated_user = user_service.authenticate(db_session, user_login)
    
    assert authenticated_user is not None
    assert authenticated_user.email == "auth@example.com"

def test_authenticate_failure(db_session: Session):
    """تست ورود با رمز عبور اشتباه."""
    user_in = UserCreate(email="fail@example.com", password="correctpass")
    user_service.create_user(db_session, user_in)
    
    user_login = UserLogin(email="fail@example.com", password="wrongpass")
    authenticated_user = user_service.authenticate(db_session, user_login)
    
    assert authenticated_user is None