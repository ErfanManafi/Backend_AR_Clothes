from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, CurrentUser, DbDependency
from app.schemas.user import UserCreate, UserLogin, UserInDB, Token, UserUpdate
from app.services.user_service import user_service

router = APIRouter()

# ------------------- ۴.۱.۱ ثبت نام (Sign Up) -------------------
@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserCreate, 
    db: DbDependency
) -> Any:
    """امکان ایجاد کاربر جدید در سامانه را فراهم می کند."""
    # بررسی وجود کاربر
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists."
        )
    
    # ایجاد کاربر
    new_user = user_service.create_user(db, user_in)
    return new_user

# ------------------- ۴.۱.۲ ورود (Login) -------------------
@router.post("/login", response_model=Token)
def login_access_token(
    db: DbDependency,
    # استفاده از OAuth2PasswordRequestForm برای دریافت username (email) و password در بدنه درخواست
    form_data: OAuth2PasswordRequestForm = Depends() 
) -> Any:
    """ورود با ایمیل و رمز عبور و دریافت توکن امنیتی JWT."""
    
    user_in = UserLogin(email=form_data.username, password=form_data.password)
    user = user_service.authenticate(db, user_in=user_in)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect email or password"
        )
    
    # ایجاد و بازگرداندن توکن
    return {
        "access_token": user_service.create_token_for_user(user),
        "token_type": "bearer",
    }
    
# ------------------- ۴.۱.۳ پروفایل کاربر -------------------
@router.get("/profile", response_model=UserInDB)
def read_user_profile(
    current_user: CurrentUser, 
    db: DbDependency
) -> Any:
    """
    مشاهده پروفایل کاربر فعلی (نیاز به توکن دارد).
    [cite_start]همچنین تعداد لباس های آپلود شده را نمایش می دهد[cite: 24].
    """
    # در اینجا می توانیم تعداد لباس های آپلود شده را محاسبه کنیم (نیازمندی پروفایل)
    uploaded_count = user_service.get_user_dresses_count(db, current_user.id)
    
    # ساخت پاسخ نهایی
    user_data = UserInDB.model_validate(current_user)
    user_data.uploaded_dress_count = uploaded_count
    
    return user_data

@router.put("/profile", response_model=UserInDB)
def update_user_profile(
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DbDependency
) -> Any:
    [cite_start]
    updated_user = user_service.update_user_profile(db, current_user, user_in)
    
    # بازیابی تعداد لباس ها برای خروجی
    uploaded_count = user_service.get_user_dresses_count(db, updated_user.id)
    user_data = UserInDB.model_validate(updated_user)
    user_data.uploaded_dress_count = uploaded_count
    
    return user_data

# ------------------- حذف اکانت (اختیاری) -------------------
# برای سادگی، فعلا عملیات حذف اکانت (۴.۱.۳) و مدیریت کاربران توسط Admin (۴.۱.۴) را حذف می کنیم.
# بعداً می توانیم آنها را اضافه کنیم.