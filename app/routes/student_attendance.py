from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.student_attendance import (
    StudentAttendanceBulk,
    StudentAttendanceRecord,
)
from app.services import student_attendance_service
from app.services.auth import get_current_user, is_admin
from app.db.database import get_database
from pymongo.database import Database

router = APIRouter()


def _require_admin(current_user: dict):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required.")


@router.post("/", response_model=dict)
async def mark_student_attendance(
    data: StudentAttendanceBulk,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin only: save the present/absent roster for a single day."""
    _require_admin(current_user)
    count = student_attendance_service.save_bulk(db, data, current_user.get("email"))
    return {"message": "Attendance saved successfully", "saved": count}


@router.get("/", response_model=List[StudentAttendanceRecord])
async def list_student_attendance(
    date: Optional[str] = Query(None, description="YYYY-MM-DD for a single day"),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin only: records for a single day (date) or a whole month (month+year)."""
    _require_admin(current_user)
    return student_attendance_service.list_attendance(
        db, date=date, month=month, year=year
    )
