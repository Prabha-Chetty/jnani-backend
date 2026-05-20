from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, date
from .py_object_id import PyObjectId


Gender = Literal["male", "female"]
Subject = Literal["kannada", "english", "hindi", "mathematics", "science", "social_science"]
Language = Literal["kannada", "english"]
ParentRelation = Literal["father", "mother", "guardian"]
AdmissionStatus = Literal["pending", "approved", "rejected"]


class AdmissionBase(BaseModel):
    # Student
    student_name: str = Field(..., max_length=100)
    father_name: str = Field(..., max_length=100)
    mother_name: str = Field(..., max_length=100)
    dob: date
    gender: Gender
    mobile_number: Optional[str] = Field(None, max_length=15)
    parent_phone: str = Field(..., max_length=15)
    email: Optional[EmailStr] = None

    # Address
    address: str = Field(..., max_length=500)
    pincode: str = Field(..., max_length=10)

    # School background
    enrolling_class: str = Field(..., max_length=20)
    current_school: Optional[str] = Field(None, max_length=200)
    board: Optional[str] = Field(None, max_length=50)
    medium: Optional[str] = Field(None, max_length=50)
    referrer: Optional[str] = Field(None, max_length=200)

    # Subjects & languages
    opted_subjects: List[Subject] = Field(default_factory=list)
    first_language: Optional[Language] = None
    second_language: Optional[Language] = None

    # Parent declaration
    parent_declaration_name: str = Field(..., max_length=200)
    parent_relation: ParentRelation
    terms_agreed: bool = Field(default=False)


class AdmissionCreate(AdmissionBase):
    pass


class AdmissionUpdate(BaseModel):
    student_name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[Gender] = None
    mobile_number: Optional[str] = None
    parent_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    enrolling_class: Optional[str] = None
    current_school: Optional[str] = None
    board: Optional[str] = None
    medium: Optional[str] = None
    referrer: Optional[str] = None
    opted_subjects: Optional[List[Subject]] = None
    first_language: Optional[Language] = None
    second_language: Optional[Language] = None
    parent_declaration_name: Optional[str] = None
    parent_relation: Optional[ParentRelation] = None
    status: Optional[AdmissionStatus] = None


class Admission(AdmissionBase):
    id: PyObjectId = Field(..., alias="_id")
    reference_no: str
    photo_url: Optional[str] = None
    student_signature_url: Optional[str] = None
    parent_signature_url: Optional[str] = None
    status: AdmissionStatus = "pending"
    submitted_at: datetime
    approved_at: Optional[datetime] = None
    converted_student_id: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True
