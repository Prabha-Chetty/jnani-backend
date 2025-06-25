from pymongo.database import Database
from app.schemas.class_schema import ClassCreate, ClassUpdate
from bson import ObjectId

def get_all_classes(db: Database):
    classes = list(db.classes.find())
    for class_item in classes:
        class_item["id"] = str(class_item["_id"])
    return classes

def create_new_class(db: Database, class_data: ClassCreate):
    class_dict = class_data.dict()
    result = db.classes.insert_one(class_dict)
    return str(result.inserted_id)

def update_class_by_id(db: Database, class_id: str, class_data: ClassUpdate):
    class_dict = class_data.dict(exclude_unset=True)
    result = db.classes.update_one(
        {"_id": ObjectId(class_id)}, {"$set": class_dict}
    )
    return result.modified_count > 0

def delete_class_by_id(db: Database, class_id: str):
    result = db.classes.delete_one({"_id": ObjectId(class_id)})
    return result.deleted_count > 0 