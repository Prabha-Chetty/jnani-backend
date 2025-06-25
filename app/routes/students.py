from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
from app.schemas.student import Student, StudentCreate, StudentUpdate
from app.services.student_service import (
    get_all_students,
    create_new_student,
    update_student_by_id,
    delete_student_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

def student_from_json(student_json: str = Form(...)) -> StudentCreate:
    try:
        data = json.loads(student_json)
        return StudentCreate(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for student data")

@router.get("/", response_model=List[Student])
async def read_students(
    db: Database = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    return get_all_students(db)

@router.post("/", response_model=dict)
async def create_student(
    student: StudentCreate = Depends(student_from_json),
    profile_image: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    student_id = create_new_student(db, student, profile_image)
    return {"message": "Student created successfully", "id": student_id}

@router.put("/{student_id}", response_model=dict)
async def update_student(
    student_id: str,
    student: StudentUpdate = Depends(student_from_json),
    profile_image: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_student_by_id(db, student_id, student, profile_image):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated successfully"}

@router.delete("/{student_id}", response_model=dict)
async def delete_student(
    student_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_student_by_id(db, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"} 