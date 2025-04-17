# tests/core/test_security.py
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# Import the functions we'll implement
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token
)
from core.config import settings

class TestSecurity:
    def test_password_hash(self):
        # Test that password hashing works
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        # Should be a bcrypt hash (starts with $2b$)
        assert hashed.startswith("$2b$")
        
    def test_password_verification(self):
        # Test that password verification works
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Correct password should verify
        assert verify_password(password, hashed) is True
        # Incorrect password should not verify
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        # Test the token creation
        data = {"sub": "user@example.com", "tenant_id": 1}
        
        # Create token with default expiration
        token = create_access_token(data)
        assert isinstance(token, str)
        
        # Decode and verify token content
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Check payload contains our data
        assert payload["sub"] == "user@example.com"
        assert payload["tenant_id"] == 1
        assert "exp" in payload
        
        # Token should expire in the future
        assert datetime.fromtimestamp(payload["exp"], tz=timezone.utc) > datetime.now(timezone.utc)
    
    def test_create_access_token_with_expiration(self):
        # Test token creation with custom expiration
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(minutes=15)
        
        # Store the time before creating the token
        before_creation = datetime.now(timezone.utc)
        
        token = create_access_token(data, expires_delta=expires_delta)
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Get expiration time from token
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Check that the expiration time is approximately 15 minutes after token creation
        # Allow for slight timing differences by checking it's within a reasonable range
        expected_min = before_creation + expires_delta - timedelta(seconds=5)
        expected_max = before_creation + expires_delta + timedelta(seconds=5)
        
        assert exp_time >= expected_min and exp_time <= expected_max
    
    def test_decode_token(self):
        # Test token decoding
        original_data = {"sub": "user@example.com", "tenant_id": 1}
        token = create_access_token(original_data)
        
        # Decode the token
        payload = decode_token(token)
        
        # Check payload contains our data
        assert payload["sub"] == "user@example.com"
        assert payload["tenant_id"] == 1
    
    def test_decode_invalid_token(self):
        # Test decoding an invalid token
        with pytest.raises(JWTError):
            decode_token("invalid.token.string")