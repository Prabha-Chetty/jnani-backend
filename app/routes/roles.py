from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.role import Role, RoleCreate
from app.services.role_service import (
    get_all_roles,
    create_new_role,
    update_role_by_id,
    delete_role_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[Role])
async def read_roles(
    db: Database = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    return get_all_roles(db)

@router.post("/", response_model=dict)
async def create_role(
    role: RoleCreate, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    role_id = create_new_role(db, role)
    return {"message": "Role created successfully", "id": role_id}

@router.put("/{role_id}", response_model=dict)
async def update_role(
    role_id: str, 
    role: RoleCreate, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_role_by_id(db, role_id, role):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role updated successfully"}

@router.delete("/{role_id}", response_model=dict)
async def delete_role(
    role_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_role_by_id(db, role_id):
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"} 