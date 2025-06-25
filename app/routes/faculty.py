from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.schemas.faculty import Faculty, FacultyCreate
from app.services.faculty_service import (
    get_all_faculties,
    create_new_faculty,
    update_faculty_by_id,
    delete_faculty_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[Faculty])
async def read_faculties(
    db: Database = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    return get_all_faculties(db)

@router.post("/", response_model=dict)
async def create_faculty(
    name: str = Form(...),
    subject: str = Form(...),
    qualification: str = Form(...),
    experience: int = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    faculty_create = FacultyCreate(
        name=name,
        subject=subject,
        qualification=qualification,
        experience=experience
    )
    faculty_id = create_new_faculty(db, faculty_create, profile_image)
    return {"message": "Faculty created successfully", "id": faculty_id}

@router.put("/{faculty_id}", response_model=dict)
async def update_faculty(
    faculty_id: str,
    name: str = Form(...),
    subject: str = Form(...),
    qualification: str = Form(...),
    experience: int = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    faculty_update = FacultyCreate(
        name=name,
        subject=subject,
        qualification=qualification,
        experience=experience,
    )
    if not update_faculty_by_id(db, faculty_id, faculty_update, profile_image):
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"message": "Faculty updated successfully"}

@router.delete("/{faculty_id}", response_model=dict)
async def delete_faculty(
    faculty_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_faculty_by_id(db, faculty_id):
        raise HTTPException(status_code=404, detail="Faculty not found")
    return {"message": "Faculty deleted successfully"} 