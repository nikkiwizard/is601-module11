from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)