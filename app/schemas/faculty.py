from pydantic import BaseModel, Field
from typing import Optional
from .py_object_id import PyObjectId

class FacultyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    subject: str = Field(..., min_length=2, max_length=50)
    qualification: str = Field(..., min_length=2, max_length=100)
    experience: int = Field(..., gt=0)
    profile_image_url: Optional[str] = None
    image_url: Optional[str] = None

class FacultyCreate(FacultyBase):
    pass

class Faculty(FacultyBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True 