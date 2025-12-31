import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# تست های API برای احراز هویت و مدیریت پروفایل

def test_api_signup_success(client: TestClient):
    """تست موفقیت آمیز ثبت نام از طریق API."""
    response = client.post(
        "/api/v1/users/signup",
        json={"email": "api@test.com", "password": "pass12345", "name": "API User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "api@test.com"
    assert "password_hash" not in data
    assert data["role"] == "user"

def test_api_login_and_get_profile(client: TestClient):
    """تست ورود و مشاهده پروفایل."""
    # ۱. ثبت نام
    client.post("/api/v1/users/signup", json={"email": "login@test.com", "password": "securepass"})
    
    # ۲. ورود (دریافت توکن)
    login_response = client.post(
        "/api/v1/users/login",
        data={"username": "login@test.com", "password": "securepass"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # ۳. مشاهده پروفایل
    profile_response = client.get("/api/v1/users/profile", headers=headers)
    assert profile_response.status_code == 200
    profile_data = profile_response.json()
    assert profile_data["email"] == "login@test.com"
    assert "uploaded_dress_count" in profile_data