import pytest

from app.models.user import User


def test_password_hashing(db_session, fake_user_data):
    original_password = "TestPass123"
    hashed_password = User.hash_password(original_password)

    user = User(
        username=fake_user_data["username"],
        email=fake_user_data["email"],
        password_hash=hashed_password,
    )

    assert user.verify_password(original_password) is True
    assert user.verify_password("WrongPass123") is False
    assert hashed_password != original_password


def test_user_registration(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123"

    user = User.register(db_session, fake_user_data)

    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.email == fake_user_data["email"]
    assert user.username == fake_user_data["username"]
    assert user.password_hash != fake_user_data["password"]
    assert user.verify_password("TestPass123") is True


def test_duplicate_user_registration(db_session):
    user1_data = {
        "username": "uniqueuser1",
        "email": "unique.test@example.com",
        "password": "TestPass123",
    }

    user2_data = {
        "username": "uniqueuser2",
        "email": "unique.test@example.com",
        "password": "TestPass123",
    }

    User.register(db_session, user1_data)
    db_session.commit()

    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)


def test_duplicate_username_registration(db_session):
    user1_data = {
        "username": "sameusername",
        "email": "first@example.com",
        "password": "TestPass123",
    }

    user2_data = {
        "username": "sameusername",
        "email": "second@example.com",
        "password": "TestPass123",
    }

    User.register(db_session, user1_data)
    db_session.commit()

    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)


def test_short_password_registration(db_session):
    test_data = {
        "username": "shortpass",
        "email": "short.pass@example.com",
        "password": "Shor1",
    }

    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)


def test_missing_password_registration(db_session):
    test_data = {
        "username": "nopassworduser",
        "email": "no.password@example.com",
    }

    with pytest.raises(ValueError, match="Password must be at least 6 characters long"):
        User.register(db_session, test_data)