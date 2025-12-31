from typing import Any, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import uuid

from app.api.deps import CurrentUser, DbDependency
from app.schemas.dress import DressInDB, DressCreate, DressUpdate
from app.services.dress_service import dress_service
from app.models.dress import Dress

router = APIRouter()

# ------------------- ۴.۲.۱ بارگذاری تصاویر -------------------
@router.post("/", response_model=DressInDB, status_code=status.HTTP_201_CREATED)
def upload_new_dress(
    db: DbDependency,
    current_user: CurrentUser,
    file: Annotated[UploadFile, File()], # دریافت فایل تصویر
    gender: Annotated[str, Form(pattern=r"^(male|female)$")], # دریافت فیلدهای متادیتا [cite: 45]
    title: Annotated[Optional[str], Form()] = None
) -> Any:
    """امکان آپلود تصویر لباس توسط کاربر را فراهم می کند."""
    
    dress_in = DressCreate(title=title, gender=gender)
    
    try:
        new_dress = dress_service.upload_dress(db, current_user, file, dress_in)
        return new_dress
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {e}")

# ------------------- ۴.۲.۵ مدیریت لیست -------------------
@router.get("/", response_model=list[DressInDB])
def list_user_dresses(
    db: DbDependency,
    current_user: CurrentUser,
    gender: Optional[str] = None # فیلتر بر اساس جنسیت (اختیاری)
) -> Any:
    """مشاهده لیست تمام لباس های آپلود شده توسط کاربر فعلی."""
    
    # می‌توانیم در اینجا از پارامتر gender برای فیلتر کردن استفاده کنیم.
    dresses = dress_service.get_user_dresses(db, current_user.id, gender=gender)
    return dresses

@router.delete("/{dress_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dress(
    dress_id: uuid.UUID,
    db: DbDependency,
    current_user: CurrentUser
) -> None:
    """حذف لباس توسط کاربر."""
    
    dress = dress_service.get_dress_by_id(db, dress_id)
    
    if not dress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dress not found.")
        
    # بررسی مالکیت (امنیت): فقط مالک می تواند حذف کند.
    if dress.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to delete this dress.")

    dress_service.delete_dress(db, dress)

# ------------------- ویرایش لباس (۴.۲.۵) -------------------
@router.put("/{dress_id}", response_model=DressInDB)
def update_dress_metadata(
    dress_id: uuid.UUID,
    dress_in: DressUpdate,
    db: DbDependency,
    current_user: CurrentUser
) -> Any:
    """ویرایش نام لباس و دسته بندی جنسیت."""
    
    dress = dress_service.get_dress_by_id(db, dress_id)
    
    if not dress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dress not found.")
        
    if dress.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to modify this dress.")
    
    # بروزرسانی مدل
    update_data = dress_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dress, key, value)
        
    db.add(dress)
    db.commit()
    db.refresh(dress)
    
    return dress