from pymongo.database import Database
from app.schemas.course import CourseCreate
from bson import ObjectId

def get_all_courses(db: Database):
    courses = list(db.courses.find())
    for course in courses:
        course["id"] = str(course["_id"])
    return courses

def create_new_course(db: Database, course: CourseCreate):
    result = db.courses.insert_one(course.dict())
    return str(result.inserted_id)

def update_course_by_id(db: Database, course_id: str, course: CourseCreate):
    result = db.courses.update_one(
        {"_id": ObjectId(course_id)}, {"$set": course.dict()}
    )
    return result.modified_count > 0

def delete_course_by_id(db: Database, course_id: str):
    result = db.courses.delete_one({"_id": ObjectId(course_id)})
    return result.deleted_count > 0 