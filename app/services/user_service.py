from pymongo.database import Database
from app.schemas.user import UserCreate, UserUpdate
from bson import ObjectId

def get_user_by_email(db: Database, email: str):
    return db.users.find_one({"email": email})

def get_all_users(db: Database):
    users = list(db.users.find())
    for user in users:
        user["id"] = str(user["_id"])
    return users

def create_new_user(db: Database, user: UserCreate):
    from app.services.auth import get_password_hash
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    result = db.users.insert_one(user_dict)
    return str(result.inserted_id)

def update_user_by_id(db: Database, user_id: str, user: UserUpdate):
    update_data = user.dict(exclude_unset=True)
    
    result = db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )
    return result.modified_count > 0

def delete_user_by_id(db: Database, user_id: str):
    result = db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0

def create_default_admin(db: Database):
    if not get_user_by_email(db, "admin@jnanituition.com"):
        admin_user = UserCreate(
            name="Admin",
            email="admin@jnanituition.com",
            password="admin123",
            is_active=True,
            roles=["admin"] # Assign a default 'admin' role
        )
        create_new_user(db, admin_user)
        print("Default admin user created.")
        
        # Also create a default admin role if it doesn't exist
        if not db.roles.find_one({"name": "admin"}):
            db.roles.insert_one({
                "name": "admin",
                "description": "Administrator with all permissions",
                "permissions": ["*"] # Wildcard for all permissions
            })
            print("Default admin role created.") 