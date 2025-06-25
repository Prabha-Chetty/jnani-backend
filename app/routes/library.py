from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional, Any
import json
from app.schemas.library import LibraryItem, LibraryItemCreate, LibraryItemUpdate
from app.services.library_service import (
    get_all_library_items,
    create_new_library_item,
    update_library_item_by_id,
    delete_library_item_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

def item_from_json(item_json: str = Form(...)) -> LibraryItemCreate:
    try:
        data = json.loads(item_json)
        return LibraryItemCreate(**data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for library item data")

@router.get("/", response_model=List[LibraryItem])
async def read_library_items(
    db: Database = Depends(get_database)
):
    return get_all_library_items(db)

@router.post("/", response_model=dict)
async def create_library_item(
    item: LibraryItemCreate = Depends(item_from_json),
    file: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    item_id = create_new_library_item(db, item, file)
    return {"message": "Library item created successfully", "id": item_id}

@router.put("/{item_id}", response_model=dict)
async def update_library_item(
    item_id: str,
    item: LibraryItemUpdate = Depends(item_from_json),
    file: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_library_item_by_id(db, item_id, item, file):
        raise HTTPException(status_code=404, detail="Library item not found")
    return {"message": "Library item updated successfully"}

@router.delete("/{item_id}", response_model=dict)
async def delete_library_item(
    item_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_library_item_by_id(db, item_id):
        raise HTTPException(status_code=404, detail="Library item not found")
    return {"message": "Library item deleted successfully"} 