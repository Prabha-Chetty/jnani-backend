from pydantic import BaseModel, Field
from typing import Optional
from .py_object_id import PyObjectId


class AttendanceCreate(BaseModel):
    date: str = Field(..., description="Attendance date in YYYY-MM-DD format")
    # Time taught is collected in whole minutes only.
    minutes_taken: int = Field(..., gt=0, le=1440)
    notes: Optional[str] = Field(None, max_length=255)
    # The faculty this entry belongs to. Required — only admins mark attendance,
    # and they must pick a faculty.
    faculty_id: str


class AttendanceUpdate(BaseModel):
    date: Optional[str] = None
    minutes_taken: Optional[int] = Field(None, gt=0, le=1440)
    notes: Optional[str] = Field(None, max_length=255)


class Attendance(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    faculty_id: str
    faculty_name: Optional[str] = None
    date: str
    day: str
    minutes_taken: int
    amount: float
    notes: Optional[str] = None
    marked_by: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class AttendanceSummaryRow(BaseModel):
    faculty_id: str
    faculty_name: Optional[str] = None
    total_minutes: int
    total_amount: float
    days: int
