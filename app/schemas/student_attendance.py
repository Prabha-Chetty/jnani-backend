from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from .py_object_id import PyObjectId


class StudentAttendanceItem(BaseModel):
    student_id: str
    status: Literal["present", "absent"]


class StudentAttendanceBulk(BaseModel):
    date: str = Field(..., description="Attendance date in YYYY-MM-DD format")
    entries: List[StudentAttendanceItem]


# Flat, per-student shape returned by the API (exploded from the per-day
# document). Storage is one document per day; this is just the read view so the
# roster and CSV keep their existing format.
class StudentAttendanceRecord(BaseModel):
    student_id: str
    date: str
    day: str
    status: Literal["present", "absent"]
    marked_by: Optional[str] = None


# Storage shape: one document per day with student ids bucketed by status.
class StudentAttendanceDay(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    date: str
    day: str
    present: List[str] = []
    absent: List[str] = []
    marked_by: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True
