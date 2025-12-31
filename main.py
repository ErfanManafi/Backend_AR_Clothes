from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

# ------------------- Routers Import -------------------
from app.api.v1.routers import users, dresses, ar_session 

# ------------------- Database Models Import -------------------
from app.db.base import Base 
from app.db.session import engine

# ------------------- Initialization Functions -------------------

def create_tables():
    """ایجاد جداول دیتابیس بر اساس مدل‌های SQLAlchemy"""
    from app.models import user, dress
    Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    """
    راه‌اندازی برنامه FastAPI همراه با مستندات حرفه‌ای و طبقه‌بندی شده
    """
    
    # ۱. ایجاد جداول دیتابیس
    try:
        create_tables() 
        print("Database tables created successfully (SQLite).")
    except Exception as e:
        print(f"Warning: Could not create database tables. Error: {e}")
    
    # ۲. تنظیمات OpenAPI و توضیحات جامع داکیومنت
    application = FastAPI(
        title="Virtual AR Fitting Room API",
        description="""
### 🚀 Comprehensive Backend Infrastructure for AR Fashion Try-On
This API serves as the backbone for a virtual fitting room application, managing user lifecycles, garment image processing, and AI engine orchestration.

#### 👤 Developer Contact:
* **Erfan Manafi (Backend Developer)**
* **LinkedIn**: [Connect on LinkedIn](https://www.linkedin.com/in/erfan-manafi-7b787a1ba/)

---

#### 🛠 Standard HTTP Response Codes & Errors:
* <b style="color: #2e7d32;">200 / 201 OK</b>: Request processed successfully.
* <b style="color: #fb8c00;">400 Bad Request</b>: Email already registered / Invalid file format (Only PNG/JPG).
* <b style="color: #fb8c00;">401 Unauthorized</b>: Invalid Bearer Token or incorrect credentials.
* <b style="color: #fb8c00;">403 Forbidden</b>: Ownership violation (modifying resources belonging to others).
* <b style="color: #fb8c00;">404 Not Found</b>: Resource (User/Dress) not found.
* <b style="color: #fb8c00;">413 Payload Too Large</b>: Image exceeds the **5MB** limit.
* <b style="color: #c62828;">500 Internal Server Error</b>: Image processing failure or AR Engine script path error.

---

#### 📖 Detailed Endpoint Documentation:

### 1. Authentication & Users
* **`GET` System Health Check**: 
    - **Description**: A simple diagnostic endpoint to verify if the server is live and the database is stable.
    - **How it works**: Returns a JSON object with the current API version and status.
* **`POST` /signup**: 
    - **Description**: Register User. Creates a new user account.
    - **How it works**: Receives email, password, and name. It hashes the password for security and stores it in the database.
* **`POST` /login**: 
    - **Description**: Login Access Token. Authenticates the user and provides a security key.
    - **How it works**: Validates credentials. If correct, generates a **JWT (JSON Web Token)** for all protected requests.
* **`GET` /profile**: 
    - **Description**: Read User Profile. Fetches account details for the logged-in user.
    - **How it works**: Decodes the Bearer Token from the header, identifies the user, and returns profile information.
* **`PUT` /profile**: 
    - **Description**: Update User Profile. Allows users to modify personal information (name/gender).

### 2. Garment Management (Dresses)
* **`POST` /dresses**: 
    - **Description**: Upload New Dress. The core image processing endpoint.
    - **How it works**: Accepts an image and metadata. It validates size (<5MB), resizes to **512x512**, ensures **Alpha Channel (Transparency)**, and saves to storage.
* **`GET` /dresses**: 
    - **Description**: List User Dresses. Displays the user's personal wardrobe collection.
* **`DELETE` /dresses/{dress_id}**: 
    - **Description**: Delete Dress. Permanently removes a garment from database and local storage.
    - **How it works**: Verifies ownership, deletes the physical file, and removes the metadata record.
* **`PUT` /dresses/{dress_id}**: 
    - **Description**: Update Dress Metadata. Edits non-image fields like title or gender category.

### 3. AR Orchestration
* **`POST` /ar-session/start**: 
    - **Description**: Start Virtual Try On. The bridge to the AI Engine.
    - **How it works**: Retrieves the dress file path, then triggers the **AI Engine (e.g., mock_ar.py)** as a background **Subprocess**, passing parameters for real-time display.

---
        """,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # ۳. متد Health Check
    @application.get("/", tags=["Health Check"], summary="Check System Status")
    def health_check():
        return {"status": "online", "message": "AR API is operational", "version": "1.0.0"}
    
    # ۴. اتصال روترها
    application.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
    application.include_router(dresses.router, prefix=f"{settings.API_V1_STR}/dresses", tags=["Dresses"])
    application.include_router(ar_session.router, prefix=f"{settings.API_V1_STR}/ar-session", tags=["AR Session"])

    # ۵. اتصال پوشه استاتیک برای نمایش عکس‌ها
    application.mount(
        "/storage/dresses", 
        StaticFiles(directory=settings.STORAGE_PATH),
        name="dresses-storage"
    )
    
    return application

app = get_application()