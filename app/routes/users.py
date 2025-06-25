from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import (
    get_all_users,
    create_new_user,
    update_user_by_id,
    delete_user_by_id,
    get_user_by_email,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    db: Database = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    return get_all_users(db)

@router.post("/", response_model=dict)
async def create_user(
    user: UserCreate, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = create_new_user(db, user)
    return {"message": "User created successfully", "id": user_id}

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str, 
    user: UserUpdate, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_user_by_id(db, user_id, user):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_user_by_id(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"} 