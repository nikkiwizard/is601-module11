from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, or_
from sqlalchemy.exc import IntegrityError

from app.auth.security import hash_password, verify_password
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)

    def __init__(self, **kwargs):
        # Accept 'password' in constructor and hash it into password_hash
        password = kwargs.pop("password", None)

        # Set simple attributes if they match columns
        for key, value in kwargs.items():
            setattr(self, key, value)

        if password is not None:
            self.password_hash = self.hash_password(password)

    def verify_password(self, plain_password: str) -> bool:
        return verify_password(plain_password, self.password_hash)

    @classmethod
    def register(cls, db, user_data):
        if not isinstance(user_data, dict):
            user_data = user_data.model_dump()

        password = user_data.get("password")

        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        existing_user = db.query(cls).filter(
            or_(
                cls.username == user_data["username"],
                cls.email == str(user_data["email"]),
            )
        ).first()

        if existing_user:
            raise ValueError("Username or email already exists")

        new_user = cls(
            username=user_data["username"],
            email=str(user_data["email"]),
            password_hash=cls.hash_password(password),
        )

        try:
            db.add(new_user)
            db.flush()
            return new_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Username or email already exists")