from fastapi import APIRouter, Depends
from typing import List
from app.schemas.permission import Permission
from app.services.permission_service import get_all_permissions
from app.services.auth import get_current_user
from app.db.database import get_database
from pymongo.database import Database

router = APIRouter()

@router.get("/", response_model=List[Permission])
async def read_permissions(
    db: Database = Depends(get_database), 
    current_user: dict = Depends(get_current_user)
):
    return get_all_permissions(db) 