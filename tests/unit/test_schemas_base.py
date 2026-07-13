import pytest
from pydantic import ValidationError

from app.schemas.base import UserCreate


def test_usercreate_requires_password():
    with pytest.raises(ValidationError):
        UserCreate(username="a", email="a@example.com", password="")


def test_usercreate_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(username="a", email="a@example.com", password="123")
