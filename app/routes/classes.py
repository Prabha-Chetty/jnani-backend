from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.class_schema import Class, ClassCreate, ClassUpdate
from app.services.class_service import (
    get_all_classes,
    create_new_class,
    update_class_by_id,
    delete_class_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[Class])
async def read_classes(
    db: Database = Depends(get_database), 
    # current_user: dict = Depends(get_current_user)
):
    return get_all_classes(db)

@router.post("/", response_model=dict)
async def create_class(
    class_data: ClassCreate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    class_id = create_new_class(db, class_data)
    return {"message": "Class created successfully", "id": class_id}

@router.put("/{class_id}", response_model=dict)
async def update_class(
    class_id: str,
    class_data: ClassUpdate,
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_class_by_id(db, class_id, class_data):
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class updated successfully"}

@router.delete("/{class_id}", response_model=dict)
async def delete_class(
    class_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_class_by_id(db, class_id):
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"} 