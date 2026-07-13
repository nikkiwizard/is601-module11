import pytest
from pydantic import ValidationError

from app.schemas.base import UserCreate


def test_user_create_valid():
    data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "SecurePass123",
    }

    user_create = UserCreate(**data)

    assert user_create.username == "johndoe"
    assert user_create.email == "john.doe@example.com"
    assert user_create.password == "SecurePass123"


def test_user_create_invalid_email():
    data = {
        "username": "johndoe",
        "email": "invalid-email",
        "password": "SecurePass123",
    }

    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_user_create_short_username():
    data = {
        "username": "jd",
        "email": "john.doe@example.com",
        "password": "SecurePass123",
    }

    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_user_create_invalid_password():
    data = {
        "username": "johndoe",
        "email": "john.doe@example.com",
        "password": "short",
    }

    with pytest.raises(ValidationError):
        UserCreate(**data)