from pymongo.database import Database
from app.schemas.faculty import FacultyCreate
from bson import ObjectId
from fastapi import UploadFile
import shutil
import os
import uuid
from typing import Optional
from datetime import datetime

MEDIA_DIR = "media"
FACULTY_IMAGES_DIR = os.path.join(MEDIA_DIR, "faculty")

# Ensure media directories exist
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(FACULTY_IMAGES_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent conflicts"""
    # Get file extension
    file_extension = os.path.splitext(original_filename)[1]
    # Generate unique name with timestamp
    unique_name = f"{uuid.uuid4()}_{int(datetime.utcnow().timestamp())}{file_extension}"
    return unique_name

def get_all_faculties(db: Database):
    faculties = list(db.faculties.find())
    for faculty in faculties:
        faculty["id"] = str(faculty["_id"])
        # Remove hardcoded localhost URL - let the frontend handle the base URL
        if faculty.get("profile_image_url"):
            # Keep the relative path as is
            pass
    return faculties

def create_new_faculty(db: Database, faculty: FacultyCreate, profile_image: Optional[UploadFile] = None):
    faculty_dict = faculty.dict()
    
    if profile_image:
        # Generate unique filename
        unique_filename = generate_unique_filename(profile_image.filename)
        file_location = os.path.join(FACULTY_IMAGES_DIR, unique_filename)
        
        # Save the file
        save_upload_file(profile_image, file_location)
        
        # Store the relative path for web access
        faculty_dict["profile_image_url"] = f"/media/faculty/{unique_filename}"

    result = db.faculties.insert_one(faculty_dict)
    return str(result.inserted_id)

def update_faculty_by_id(db: Database, faculty_id: str, faculty: FacultyCreate, profile_image: Optional[UploadFile] = None):
    faculty_dict = faculty.dict(exclude_unset=True)

    if profile_image:
        # Delete the old image before saving the new one
        old_faculty = db.faculties.find_one({"_id": ObjectId(faculty_id)})
        if old_faculty and old_faculty.get("profile_image_url"):
            # Construct file system path from web path
            old_image_path = old_faculty["profile_image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        # Generate unique filename for new image
        unique_filename = generate_unique_filename(profile_image.filename)
        file_location = os.path.join(FACULTY_IMAGES_DIR, unique_filename)
        
        # Save the new file
        save_upload_file(profile_image, file_location)
        faculty_dict["profile_image_url"] = f"/media/faculty/{unique_filename}"
    
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