from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, CurrentUser, DbDependency
from app.schemas.user import UserCreate, UserLogin, UserInDB, Token, UserUpdate
from app.services.user_service import user_service

router = APIRouter()

# ------------------- ۴.۱.۱ ثبت نام (Sign Up) -------------------
@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED, summary="Register User", description="""
<b style="color: #2e7d32;">POST</b>: **Account Creation**.
- **Logic**: Receives `email`, `password`, and `name`. It hashes the password for security and stores the user in the database.
- **Errors**: Returns 400 if the email is already registered.
""")
def register_user(
    user_in: UserCreate, 
    db: DbDependency
) -> Any:
    """امکان ایجاد کاربر جدید در سامانه را فراهم می کند."""
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists."
        )
    
    new_user = user_service.create_user(db, user_in)
    return new_user

# ------------------- ۴.۱.۲ ورود (Login) -------------------
@router.post("/login", response_model=Token, summary="Login Access Token", description="""
<b style="color: #2e7d32;">POST</b>: **Authentication**.
- **Logic**: Validates credentials. If correct, generates a **JWT (JSON Web Token)** for secure session management.
- **Errors**: Returns 400 for incorrect email or password.
""")
def login_access_token(
    db: DbDependency,
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
    
    return {
        "access_token": user_service.create_token_for_user(user),
        "token_type": "bearer",
    }
    
# ------------------- ۴.۱.۳ پروفایل کاربر -------------------
@router.get("/profile", response_model=UserInDB, summary="Read User Profile", description="""
<b style="color: #0277bd;">GET</b>: **Data Retrieval**.
- **Logic**: Decodes the Bearer Token to identify the user and returns profile information including the total count of uploaded garments.
""")
def read_user_profile(
    current_user: CurrentUser, 
    db: DbDependency
) -> Any:
    """مشاهده پروفایل کاربر فعلی (نیاز به توکن دارد)."""
    uploaded_count = user_service.get_user_dresses_count(db, current_user.id)
    
    user_data = UserInDB.model_validate(current_user)
    user_data.uploaded_dress_count = uploaded_count
    
    return user_data

@router.put("/profile", response_model=UserInDB, summary="Update User Profile", description="""
<b style="color: #ef6c00;">PUT</b>: **Data Modification**.
- **Logic**: Allows the authenticated user to update personal fields like `name` or `gender`.
""")
def update_user_profile(
    user_in: UserUpdate,
    current_user: CurrentUser,
    db: DbDependency
) -> Any:
    updated_user = user_service.update_user_profile(db, current_user, user_in)
    
    uploaded_count = user_service.get_user_dresses_count(db, updated_user.id)
    user_data = UserInDB.model_validate(updated_user)
    user_data.uploaded_dress_count = uploaded_count
    
    return user_data

# ------------------- ۴.۱.۴ حذف اکانت -------------------
@router.delete("/me", summary="Delete My Account", description="""
<b style="color: #c62828;">DELETE</b>: **Account Removal**.
- **Logic**: Permanently deletes the authenticated user's account and all associated data from the database.
- **Security**: This action is irreversible and requires a valid Bearer Token.
""")
def delete_user_account(
    current_user: CurrentUser, 
    db: DbDependency
) -> Any:
    """حذف دائمی حساب کاربری کاربر فعلی."""
    user_service.delete_user(db, user_id=current_user.id)
    return {"message": "User account and all associated data deleted successfully."}