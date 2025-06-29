from pymongo.database import Database
from app.schemas.student import StudentCreate, StudentUpdate
from bson import ObjectId
from fastapi import UploadFile
import shutil
import os
from typing import Optional
from app.config import settings

MEDIA_DIR = "media"

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

def get_all_students(db: Database):
    students = list(db.students.find())
    for student in students:
        student["id"] = str(student["_id"])
        if student.get("profile_image_url"):
            student["profile_image_url"] = f"{settings.MEDIA_URL}{student['profile_image_url']}"
    return students

def create_new_student(db: Database, student: StudentCreate, profile_image: Optional[UploadFile] = None):
    student_dict = student.dict()
    
    if profile_image:
        filename = profile_image.filename
        file_location = os.path.join(MEDIA_DIR, filename)
        save_upload_file(profile_image, file_location)
        student_dict["profile_image_url"] = f"/media/{filename}"

    result = db.students.insert_one(student_dict)
    return str(result.inserted_id)

def update_student_by_id(db: Database, student_id: str, student: StudentUpdate, profile_image: Optional[UploadFile] = None):
    student_dict = student.dict(exclude_unset=True)

    if profile_image:
        old_student = db.students.find_one({"_id": ObjectId(student_id)})
        if old_student and old_student.get("profile_image_url"):
            old_image_path = old_student["profile_image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        filename = profile_image.filename
        file_location = os.path.join(MEDIA_DIR, filename)
        save_upload_file(profile_image, file_location)
        student_dict["profile_image_url"] = f"/media/{filename}"
    
    result = db.students.update_one(
        {"_id": ObjectId(student_id)}, {"$set": student_dict}
    )
    return result.modified_count > 0

def delete_student_by_id(db: Database, student_id: str):
    student = db.students.find_one({"_id": ObjectId(student_id)})
    if student and student.get("profile_image_url"):
        image_path = student["profile_image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
        if os.path.exists(image_path):
            os.remove(image_path)
            
    result = db.students.delete_one({"_id": ObjectId(student_id)})
    return result.deleted_count > 0 