from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from .py_object_id import PyObjectId

class StudentBase(BaseModel):
    name: str = Field(..., max_length=100)
    class_name: str = Field(..., max_length=50)
    parent_name: str = Field(..., max_length=100)
    contact_number: str = Field(..., max_length=15)
    profile_image_url: Optional[str] = None
    image_url: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class Student(StudentBase):
    id: PyObjectId = Field(..., alias="_id")
    joined_date: Optional[datetime] = None

    class Config:
        populate_by_name = True
        from_attributes = True 