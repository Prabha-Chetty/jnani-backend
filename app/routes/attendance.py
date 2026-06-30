from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.attendance import (
    Attendance,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceSummaryRow,
)
from app.services import attendance_service
from app.services.auth import get_current_user, is_admin
from app.config import settings
from app.db.database import get_database
from pymongo.database import Database

router = APIRouter()


def _require_admin(current_user: dict):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required.")


@router.get("/config", response_model=dict)
async def attendance_config(current_user: dict = Depends(get_current_user)):
    """Remuneration config used by the UI to preview/compute amounts."""
    return {
        "rate_per_class": settings.RATE_PER_CLASS,
        "class_minutes": settings.CLASS_MINUTES,
    }


@router.post("/", response_model=dict)
async def mark_attendance(
    data: AttendanceCreate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin only: record an attendance entry for the selected faculty."""
    _require_admin(current_user)
    attendance_id = attendance_service.create_attendance(
        db, data.faculty_id, data, current_user.get("email")
    )
    return {"message": "Attendance recorded successfully", "id": attendance_id}


@router.get("/", response_model=List[Attendance])
async def all_attendance(
    faculty_id: Optional[str] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin: list attendance across all faculties, optionally filtered."""
    _require_admin(current_user)
    return attendance_service.list_attendance(
        db, faculty_id=faculty_id, month=month, year=year
    )


@router.get("/summary", response_model=List[AttendanceSummaryRow])
async def attendance_summary(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin: total minutes, amount and days per faculty for the period."""
    _require_admin(current_user)
    return attendance_service.summary(db, month=month, year=year)


@router.put("/{attendance_id}", response_model=dict)
async def update_attendance(
    attendance_id: str,
    data: AttendanceUpdate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin only: edit an attendance entry."""
    _require_admin(current_user)
    if not attendance_service.update_attendance(db, attendance_id, data):
        raise HTTPException(status_code=404, detail="Attendance entry not found.")
    return {"message": "Attendance updated successfully"}


@router.delete("/{attendance_id}", response_model=dict)
async def delete_attendance(
    attendance_id: str,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user),
):
    """Admin only: delete an attendance entry."""
    _require_admin(current_user)
    if not attendance_service.delete_attendance(db, attendance_id):
        raise HTTPException(status_code=404, detail="Attendance entry not found.")
    return {"message": "Attendance deleted successfully"}
