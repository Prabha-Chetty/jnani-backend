from pydantic import BaseModel, Field
from typing import List, Optional
from .py_object_id import PyObjectId

class CourseBase(BaseModel):
    name: str
    description: str
    class_level: str
    subjects: List[str]
    duration: str
    fee: float
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True 