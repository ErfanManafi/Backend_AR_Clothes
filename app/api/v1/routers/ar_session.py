from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from app.api.deps import CurrentUser, DbDependency
from app.schemas.dress import ARSessionCreate, ARSessionStatus
from app.services.ar_orchestrator import ar_orchestrator
from app.services.dress_service import dress_service
from app.models.dress import Dress

router = APIRouter()

# ------------------- ۴.۳.۱ و ۴.۳.۲ اجرای کد پایتون -------------------
@router.post("/start", response_model=ARSessionStatus)
def start_virtual_try_on(
    session_in: ARSessionCreate, 
    db: DbDependency,
    current_user: CurrentUser
) -> Any:
    """
    کاربر روی دکمه 'اجرای اتاق پرو مجازی' کلیک می کند و موتور AR اجرا می شود.
    """
    
    # ۱. بازیابی لباس انتخاب شده
    dress = dress_service.get_dress_by_id(db, session_in.dress_id)
    
    if not dress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Selected dress not found.")
        
    # ۲. بررسی مالکیت (امنیت)
    if dress.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot run AR for a dress you didn't upload.")

    # ۳. شروع فرآیند AR
    session_status = ar_orchestrator.start_ar_session(db, dress)
    
    return session_status