# tests/schemas/auth/test_login.py
import pytest
from pydantic import ValidationError
from schemas.auth.login import LoginRequest

class TestLoginSchema:
    def test_valid_login_request(self):
        # Test valid login request
        data = {
            "email": "user@example.com",
            "password": "securepassword123"
        }
        login_request = LoginRequest(**data)
        assert login_request.email == data["email"]
        assert login_request.password == data["password"]
    
    def test_invalid_email_format(self):
        # Test invalid email format
        with pytest.raises(ValidationError):
            LoginRequest(email="invalid-email", password="securepassword123")
    
    def test_empty_password(self):
        # Test empty password
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="")