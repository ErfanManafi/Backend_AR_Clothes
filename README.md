# 🚀 Virtual AR Fitting Room API

A high-performance FastAPI backend infrastructure designed for virtual try-on systems. This project serves as the bridge between user management, garment processing, and AI-driven AR engines.

---

## 👨‍💻 Developed By
**Erfan Manafi** [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/erfan-manafi-7b787a1ba/)

---

## 📌 Key Features
- **User Authentication**: Secure signup and login using OAuth2 and JWT tokens.
- **Image Processing Pipeline**: Automatic resizing (512x512) and Alpha-channel optimization for garment images.
- **AR Orchestration**: Non-blocking subprocess management to trigger external AI engines (AI/AR Integration).
- **Comprehensive Documentation**: Professional Swagger UI with detailed logic and error descriptions.

## 🛠 Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy (SQLite)
- **Image Processing**: Pillow (PIL)
- **Security**: JWT & Bcrypt

---

## 📖 API Documentation Overview

### 🛠 Standard HTTP Response Codes & Errors:
* **200 / 201 OK**: Request processed successfully.
* **400 Bad Request**: Email already registered / Invalid file format (Only PNG/JPG).
* **401 Unauthorized**: Invalid Bearer Token or incorrect credentials.
* **403 Forbidden**: Ownership violation (modifying resources belonging to others).
* **404 Not Found**: Resource (User/Dress) not found.
* **413 Payload Too Large**: Image exceeds the **5MB** limit.
* **500 Internal Server Error**: Image processing failure or AR Engine script path error.

### 1. Authentication & Users
* **`GET /`**: System Health Check - Verifies server & database status.
* **`POST /signup`**: Register a new user with hashed password security.
* **`POST /login`**: Exchange credentials for a JWT Access Token.
* **`GET /profile`**: Retrieve authenticated user details via Bearer Token.

### 2. Garment Management (Dresses)
* **`POST /api/v1/dresses`**: Upload and process garment images (Auto-resize & Transparency).
* **`GET /api/v1/dresses`**: List all garments associated with the user account.
* **`DELETE /api/v1/dresses/{id}`**: Securely remove garment records and physical files.

### 3. AR Orchestration
* **`POST /api/v1/ar-session/start`**: Triggers the AI Engine (`mock_ar.py`) as a background subprocess with specific dress paths.

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-link>
   cd <repo-folder>

## ⚙️ Create a virtual environment

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

## ⚙️ Install dependencies

pip install -r requirements.txt

## ⚙️ Run the server

uvicorn main:app --reload --port 8080