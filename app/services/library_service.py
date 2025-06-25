from pymongo.database import Database
from app.schemas.library import LibraryItemCreate, LibraryItemUpdate
from bson import ObjectId
from fastapi import UploadFile
import shutil
import os
from typing import Optional

MEDIA_DIR = "media"

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

def get_all_library_items(db: Database):
    items = list(db.library.find())
    print("Raw items from DB:", items)
    for item in items:
        item["id"] = str(item["_id"])
        del item["_id"]
        if item.get("file_url"):
            item["file_url"] = f"http://localhost:8000{item['file_url']}"
    print("Processed items:", items)
    return items

def create_new_library_item(db: Database, item: LibraryItemCreate, file: Optional[UploadFile] = None):
    item_dict = item.dict()
    
    if file:
        file_location = os.path.join(MEDIA_DIR, file.filename)
        save_upload_file(file, file_location)
        item_dict["file_url"] = f"/media/{file.filename}"

    result = db.library.insert_one(item_dict)
    return str(result.inserted_id)

def update_library_item_by_id(db: Database, item_id: str, item: LibraryItemUpdate, file: Optional[UploadFile] = None):
    item_dict = item.dict(exclude_unset=True)
    
    old_item = db.library.find_one({"_id": ObjectId(item_id)})

    if file:
        if old_item and old_item.get("file_url"):
            old_file_path = old_item["file_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        file_location = os.path.join(MEDIA_DIR, file.filename)
        save_upload_file(file, file_location)
        item_dict["file_url"] = f"/media/{file.filename}"
    
    result = db.library.update_one(
        {"_id": ObjectId(item_id)}, {"$set": item_dict}
    )
    return result.modified_count > 0

def delete_library_item_by_id(db: Database, item_id: str):
    item = db.library.find_one({"_id": ObjectId(item_id)})
    if item and item.get("file_url"):
        file_path = item["file_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    result = db.library.delete_one({"_id": ObjectId(item_id)})
    return result.deleted_count > 0 