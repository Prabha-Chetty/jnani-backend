from pymongo.database import Database
from app.schemas.role import RoleCreate
from bson import ObjectId

def get_all_roles(db: Database):
    roles = list(db.roles.find())
    for role in roles:
        role["id"] = str(role["_id"])
    return roles

def create_new_role(db: Database, role: RoleCreate):
    result = db.roles.insert_one(role.dict())
    return str(result.inserted_id)

def update_role_by_id(db: Database, role_id: str, role: RoleCreate):
    result = db.roles.update_one(
        {"_id": ObjectId(role_id)}, {"$set": role.dict()}
    )
    return result.modified_count > 0

def delete_role_by_id(db: Database, role_id: str):
    result = db.roles.delete_one({"_id": ObjectId(role_id)})
    return result.deleted_count > 0 