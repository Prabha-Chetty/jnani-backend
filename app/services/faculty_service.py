from pymongo.database import Database
from app.schemas.faculty import FacultyCreate
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

def get_all_faculties(db: Database):
    faculties = list(db.faculties.find())
    for faculty in faculties:
        faculty["id"] = str(faculty["_id"])
        if faculty.get("profile_image_url"):
             # The URL is already stored with the /media path, so just prepend the base
             faculty["profile_image_url"] = f"http://localhost:8000{faculty['profile_image_url']}"
    return faculties

def create_new_faculty(db: Database, faculty: FacultyCreate, profile_image: Optional[UploadFile] = None):
    faculty_dict = faculty.dict()
    
    if profile_image:
        # Ensure filename is secure
        filename = profile_image.filename
        file_location = os.path.join(MEDIA_DIR, filename)
        save_upload_file(profile_image, file_location)
        # Store a web-accessible path, not a file system path
        faculty_dict["profile_image_url"] = f"/media/{filename}"

    result = db.faculties.insert_one(faculty_dict)
    return str(result.inserted_id)

def update_faculty_by_id(db: Database, faculty_id: str, faculty: FacultyCreate, profile_image: Optional[UploadFile] = None):
    faculty_dict = faculty.dict(exclude_unset=True)

    if profile_image:
        # Optionally, delete the old image before saving the new one
        old_faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
        if old_faculty and old_faculty.get("profile_image_url"):
            # Construct file system path from web path
            old_image_path = old_faculty["profile_image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        filename = profile_image.filename
        file_location = os.path.join(MEDIA_DIR, filename)
        save_upload_file(profile_image, file_location)
        faculty_dict["profile_image_url"] = f"/media/{filename}"
    
    result = db.faculties.update_one(
        {"_id": ObjectId(faculty_id)}, {"$set": faculty_dict}
    )
    return result.modified_count > 0

def delete_faculty_by_id(db: Database, faculty_id: str):
    # Also delete the associated image file
    faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
    if faculty and faculty.get("profile_image_url"):
        image_path = faculty["profile_image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
        if os.path.exists(image_path):
            os.remove(image_path)
            
    result = db.faculties.delete_one({"_id": ObjectId(faculty_id)})
    return result.deleted_count > 0 