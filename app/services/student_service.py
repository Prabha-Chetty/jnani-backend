from pymongo.database import Database
from app.schemas.student import StudentCreate, StudentUpdate
from app.services import cloudinary_service
from bson import ObjectId
from fastapi import UploadFile
from typing import Optional


def _is_cloudinary_url(url: Optional[str]) -> bool:
    return bool(url) and url.startswith("https://res.cloudinary.com/")


def get_all_students(db: Database):
    students = list(db.students.find())
    for student in students:
        student["id"] = str(student["_id"])
        # Legacy local /media URLs are dead on Render — return as-is, the frontend
        # falls back to the avatar initial when the image fails to load.
    return students


def create_new_student(
    db: Database, student: StudentCreate, profile_image: Optional[UploadFile] = None
):
    student_dict = student.dict()

    if profile_image:
        uploaded = cloudinary_service.upload_file(profile_image, folder="students/photos")
        student_dict["profile_image_url"] = uploaded["url"]
        student_dict["profile_image_public_id"] = uploaded["public_id"]

    result = db.students.insert_one(student_dict)
    return str(result.inserted_id)


def update_student_by_id(
    db: Database,
    student_id: str,
    student: StudentUpdate,
    profile_image: Optional[UploadFile] = None,
):
    student_dict = student.dict(exclude_unset=True)

    if profile_image:
        old = db.students.find_one({"_id": ObjectId(student_id)})
        if old and old.get("profile_image_public_id"):
            cloudinary_service.delete_by_public_id(old["profile_image_public_id"])

        uploaded = cloudinary_service.upload_file(profile_image, folder="students/photos")
        student_dict["profile_image_url"] = uploaded["url"]
        student_dict["profile_image_public_id"] = uploaded["public_id"]

    result = db.students.update_one(
        {"_id": ObjectId(student_id)}, {"$set": student_dict}
    )
    return result.modified_count > 0


def delete_student_by_id(db: Database, student_id: str):
    student = db.students.find_one({"_id": ObjectId(student_id)})
    if student and student.get("profile_image_public_id"):
        cloudinary_service.delete_by_public_id(student["profile_image_public_id"])

    result = db.students.delete_one({"_id": ObjectId(student_id)})
    return result.deleted_count > 0
