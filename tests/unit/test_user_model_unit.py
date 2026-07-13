import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User
from app.database import Base


@pytest.fixture
def in_memory_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        yield s
    finally:
        s.close()


def test_user_init_and_verify(in_memory_session):
    u = User(username="u1", email="u1@example.com", password="password123")
    assert hasattr(u, "password_hash")
    assert u.verify_password("password123")


def test_register_short_password_raises(in_memory_session):
    data = {"username": "x", "email": "x@example.com", "password": "123"}
    with pytest.raises(ValueError):
        User.register(in_memory_session, data)


def test_register_duplicate_raises(in_memory_session):
    data = {"username": "dup", "email": "dup@example.com", "password": "TestPass123"}
    u = User.register(in_memory_session, data)
    in_memory_session.commit()
    with pytest.raises(ValueError):
        User.register(in_memory_session, data)


def test_register_with_pydantic_like_object(in_memory_session):
    class FakeModel:
        def __init__(self, data):
            self._data = data

        def model_dump(self):
            return self._data

    data = {"username": "pm", "email": "pm@example.com", "password": "TestPass123"}
    fm = FakeModel(data)
    u = User.register(in_memory_session, fm)
    assert u.username == "pm"


def test_register_handles_integrityerror_and_rolls_back():
    # create a fake session that will raise IntegrityError on flush
    class DummyQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeSession:
        def __init__(self):
            self.rolled_back = False

        def query(self, cls):
            return DummyQuery()

        def add(self, obj):
            pass

        def flush(self):
            from sqlalchemy.exc import IntegrityError

            raise IntegrityError("msg", params=None, orig=None)

        def rollback(self):
            self.rolled_back = True

    fs = FakeSession()
    data = {"username": "x", "email": "x@example.com", "password": "TestPass123"}
    with pytest.raises(ValueError):
        User.register(fs, data)
