from pydantic import BaseModel, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def validate_password(cls, values):
        password = values.get("password")

        if not password:
            raise ValueError("Password is required")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")

        return values