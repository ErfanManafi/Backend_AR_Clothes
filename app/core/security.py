from datetime import datetime, timedelta
from typing import Any, Union, Optional
from passlib.context import CryptContext
from jose import jwt, JWTError

from app.core.config import settings

# اصلاح: حذف 'deprecated="auto"' برای جلوگیری از خطای طول رمز عبور در تست‌ها
pwd_context = CryptContext(schemes=["bcrypt"])

# ------------------- توابع هش و اعتبارسنجی رمز عبور -------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی می کند که آیا رمز عبور ورودی با رمز عبور هش شده مطابقت دارد."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """رمز عبور را هش می کند."""
    return pwd_context.hash(password)

# ------------------- توابع JWT -------------------

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """یک توکن دسترسی JWT ایجاد می کند."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """توکن دسترسی JWT را دیکد می کند."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None