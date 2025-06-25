from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.course import Course, CourseCreate
from app.services.course_service import (
    get_all_courses,
    create_new_course,
    update_course_by_id,
    delete_course_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[Course])
async def read_courses(db: Database = Depends(get_database)):
    return get_all_courses(db)

@router.post("/", response_model=dict)
async def create_course(
    course: CourseCreate, 
    db: Database = Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    course_id = create_new_course(db, course)
    return {"message": "Course created successfully", "id": course_id}

@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str, 
    course: CourseCreate, 
    db: Database = Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    if not update_course_by_id(db, course_id, course):
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course updated successfully"}

@router.delete("/{course_id}", response_model=dict)
async def delete_course(
    course_id: str, 
    db: Database = Depends(get_database),
    current_user: str = Depends(get_current_user)
):
    if not delete_course_by_id(db, course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"} 