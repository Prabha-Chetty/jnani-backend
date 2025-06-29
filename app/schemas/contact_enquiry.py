from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from .py_object_id import PyObjectId

class ContactEnquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    message: str = Field(..., min_length=10, max_length=1000)

class ContactEnquiryUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|read|replied|closed)$")
    admin_notes: Optional[str] = None

class ContactEnquiry(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    name: str
    email: str
    phone: str
    message: str
    status: str = "pending"  # pending, read, replied, closed
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True 