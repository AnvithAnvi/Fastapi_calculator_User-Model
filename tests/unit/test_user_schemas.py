# tests/unit/test_user_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas import UserCreate

def test_user_create_valid():
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
    )
    assert user.username == "testuser"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="not-an-email",
            password="password123",
        )
