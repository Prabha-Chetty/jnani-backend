from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from .py_object_id import PyObjectId

class UserBase(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True
    roles: List[str] = []

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None
    password: Optional[str] = None

class User(UserBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60d0fe4f5311236168a109ca",
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "is_active": True,
                "roles": ["user"]
            }
        }

class UserInDB(UserBase):
    hashed_password: str

class AdminLogin(BaseModel):
    email: str
    password: str 