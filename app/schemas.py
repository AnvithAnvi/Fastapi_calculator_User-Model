
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, ConfigDict

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=6, max_length=72)  # bcrypt max ~72 bytes

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    # Pydantic v2 replacement for orm_mode=True
    model_config = ConfigDict(from_attributes=True)
