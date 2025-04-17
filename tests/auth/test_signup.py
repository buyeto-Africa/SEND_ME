# tests/auth/test_signup.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from main import app

def test_signup(client: TestClient):
    # Test the user signup with valid data
    response = client.post(
        "/auth/signup/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "phone_number": "1234567890",
            "tenant_id": 1  # Assuming tenant 1 exists
        },
    )
    
    # Assert the response is as expected (success status code)
    assert response.status_code == 201
    assert response.json() == {"msg": "User created successfully"}

def test_signup_existing_user(client: TestClient):
    # Register the user first
    client.post(
        "/auth/signup/",
        json={
            "email": "existing@example.com", 
            "password": "securepassword123", 
            "phone_number": "1234567890",
            "tenant_id": 1
        },
    )

    # Try to register the same user again and expect an error
    response = client.post(
        "/auth/signup/",
        json={
            "email": "existing@example.com", 
            "password": "anotherpassword", 
            "tenant_id": 1
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}