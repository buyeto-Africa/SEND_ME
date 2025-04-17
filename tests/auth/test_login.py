# tests/auth/test_login.py
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from models.user import User
from core.security import get_password_hash

# Password context for hashing in tests
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_login_success(client: TestClient, db: Session):
    # Create a test user
    hashed_password = get_password_hash("testpassword123")
    test_user = User(
        email="testuser@example.com",
        password=hashed_password,
        tenant_id=1,
        role="customer",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Test login
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "testpassword123"
        },
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == test_user.id
    assert data["role"] == "customer"
    assert data["tenant_id"] == 1

def test_login_invalid_credentials(client: TestClient, db: Session):
    # Create a test user
    hashed_password = get_password_hash("testpassword123")
    test_user = User(
        email="testuser2@example.com",
        password=hashed_password,
        tenant_id=1,
        role="customer",
        is_active=True
    )
    db.add(test_user)
    db.commit()
    
    # Test login with wrong password
    response = client.post(
        "/auth/login",
        json={
            "email": "testuser2@example.com",
            "password": "wrongpassword"
        },
    )
    
    # Check response
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

def test_login_inactive_user(client: TestClient, db: Session):
    # Create an inactive test user
    hashed_password = get_password_hash("testpassword123")
    test_user = User(
        email="inactive@example.com",
        password=hashed_password,
        tenant_id=1,
        role="customer",
        is_active=False
    )
    db.add(test_user)
    db.commit()
    
    # Test login with inactive user
    response = client.post(
        "/auth/login",
        json={
            "email": "inactive@example.com",
            "password": "testpassword123"
        },
    )
    
    # Check response
    assert response.status_code == 401
    assert response.json() == {"detail": "Inactive user"}

def test_login_nonexistent_user(client: TestClient):
    # Test login with non-existent user
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        },
    )
    
    # Check response
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}