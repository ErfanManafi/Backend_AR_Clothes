from typing import Generator, Annotated, Optional # Optional اضافه شد
import uuid # برای استفاده از uuid در صورت نیاز

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import SessionLocal 
from app.core.config import settings
from app.core.security import decode_access_token 
from app.models.user import User
from app.schemas.user import UserInDB 

# تعریف طرح امنیتی OAuth2 (از نوع Bearer Token)
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/users/login"
)

# ------------------- Dependencies دیتابیس -------------------

def get_db() -> Generator[Session, None, None]: # type hint دقیق تر شد
    """Dependency برای دریافت Session دیتابیس"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
DbDependency = Annotated[Session, Depends(get_db)]

# ------------------- Dependencies احراز هویت -------------------

def get_current_user(
    db: DbDependency, 
    token: str = Depends(reusable_oauth2)
) -> User:
    """کاربر فعلی را با استفاده از توکن JWT بازیابی می کند."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token=token)
    if payload is None:
        raise credentials_exception
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    # تبدیل رشته user_id به UUID برای استفاده در کوئری
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user

# ------------------- Dependencies نقش ها -------------------

def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """بررسی می کند که آیا کاربر فعلی ادمین است."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges (Admin role required)"
        )
    return current_user

# ------------------- Alias های نقش ها -------------------
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]