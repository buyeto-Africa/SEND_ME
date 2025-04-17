# tests/core/test_deps.py
import pytest
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.security import create_access_token
from core.deps import get_current_user, get_current_active_user, RoleChecker
from core.config import settings
from models.user import User
from core.database import Base, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Sample app for testing dependencies
app = FastAPI()

# Override the get_db dependency for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create role checker for testing
allow_customer = RoleChecker(["customer"])
allow_tenant_admin = RoleChecker(["tenant_admin"])
allow_platform_admin = RoleChecker(["platform_admin"])
allow_multiple = RoleChecker(["customer", "tenant_admin"])

@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "email": current_user.email, "role": current_user.role}

@app.get("/users/me/active")
def read_users_me_active(current_user: User = Depends(get_current_active_user)):
    return {"user_id": current_user.id, "email": current_user.email, "role": current_user.role}

@app.get("/customers-only")
def customers_only(current_user: User = Depends(allow_customer)):
    return {"access": "granted", "role": current_user.role}

@app.get("/tenant-admin-only")
def tenant_admin_only(current_user: User = Depends(allow_tenant_admin)):
    return {"access": "granted", "role": current_user.role}

@app.get("/platform-admin-only")
def platform_admin_only(current_user: User = Depends(allow_platform_admin)):
    return {"access": "granted", "role": current_user.role}

@app.get("/customer-or-tenant")
def customer_or_tenant(current_user: User = Depends(allow_multiple)):
    return {"access": "granted", "role": current_user.role}


# Test fixtures and utilities
def create_test_token(user_id=1, email="test@example.com", role="customer", tenant_id=1, expired=False):
    expire_minutes = -5 if expired else 30
    expires_delta = timedelta(minutes=expire_minutes)
    data = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "tenant_id": tenant_id
    }
    return create_access_token(data, expires_delta)


class TestUserDependency:
    def setup_method(self):
        # Create test database tables
        Base.metadata.create_all(bind=test_engine)
        
        # Create test client
        self.client = TestClient(app)
        
        # Create test users in the database
        db = TestingSessionLocal()
        
        # Active test user (customer)
        test_user = User(
            id=1,
            email="test@example.com",
            password="hashed_password",
            phone_number="1234567890",
            tenant_id=1,
            role="customer",
            is_active=True
        )
        db.add(test_user)
        
        # Inactive test user
        inactive_user = User(
            id=2,
            email="inactive@example.com",
            password="hashed_password",
            phone_number="1234567890",
            tenant_id=1,
            role="customer",
            is_active=False
        )
        db.add(inactive_user)
        
        # Tenant admin user
        admin_user = User(
            id=3,
            email="admin@example.com",
            password="hashed_password",
            phone_number="1234567890",
            tenant_id=1,
            role="tenant_admin",
            is_active=True
        )
        db.add(admin_user)
        
        # Platform admin user
        platform_admin = User(
            id=4,
            email="platform@example.com",
            password="hashed_password",
            phone_number="1234567890",
            tenant_id=1,
            role="platform_admin",
            is_active=True
        )
        db.add(platform_admin)
        
        db.commit()
        db.close()
    
    def teardown_method(self):
        # Drop all tables after each test
        Base.metadata.drop_all(bind=test_engine)
    
    # Your existing test methods remain the same
    def test_get_current_user_valid_token(self):
        token = create_test_token()
        response = self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "customer"
    
    def test_get_current_user_no_token(self):
        response = self.client.get("/users/me")
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}
    
    def test_get_current_user_invalid_token(self):
        response = self.client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Could not validate credentials"}
    
    def test_get_current_user_expired_token(self):
        token = create_test_token(expired=True)
        response = self.client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Token has expired"}
    
    def test_get_current_active_user(self):
        token = create_test_token()
        response = self.client.get(
            "/users/me/active",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
    
    def test_role_checker_allowed_role(self):
        token = create_test_token(role="customer")
        response = self.client.get(
            "/customers-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"access": "granted", "role": "customer"}
    
    def test_role_checker_forbidden_role(self):
        token = create_test_token(role="customer")
        response = self.client.get(
            "/tenant-admin-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Insufficient permissions"}
    
    def test_role_checker_multiple_allowed_roles(self):
        # Test with customer role
        token = create_test_token(role="customer")
        response = self.client.get(
            "/customer-or-tenant",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Test with tenant_admin role
        token = create_test_token(role="tenant_admin")
        response = self.client.get(
            "/customer-or-tenant",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200