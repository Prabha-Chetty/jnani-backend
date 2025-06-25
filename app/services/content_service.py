from pymongo.database import Database
from app.schemas.content import ContentCreate
from bson import ObjectId

def get_all_content(db: Database):
    content_list = list(db.content.find())
    
    # Transform the content into the desired format
    structured_content = {
        "about_us": "",
        "mission": "",
        "vision": "",
        "values": [],
        "contact_us": {
            "phone": "",
            "address": ""
        },
        "map_link": "",
        "social_media": {
            "facebook": "",
            "youtube": "",
            "instagram": "",
            "twitter": "",
            "linkedin": "",
            "whatsapp": ""
        }
    }
    
    for item in content_list:
        content_type = item.get("type", "")
        
        if content_type == "about":
            structured_content["about_us"] = item.get("description", "")
            structured_content["mission"] = item.get("mission", "")
            structured_content["vision"] = item.get("vision", "")
            structured_content["values"] = item.get("values", [])
        elif content_type == "contact":
            structured_content["contact_us"]["phone"] = item.get("phone", "")
            structured_content["contact_us"]["address"] = item.get("address", "")
            structured_content["map_link"] = item.get("map_link", "")
        elif content_type == "social_media":
            structured_content["social_media"]["facebook"] = item.get("facebook", "")
            structured_content["social_media"]["youtube"] = item.get("youtube", "")
            structured_content["social_media"]["instagram"] = item.get("instagram", "")
            structured_content["social_media"]["twitter"] = item.get("twitter", "")
            structured_content["social_media"]["linkedin"] = item.get("linkedin", "")
            structured_content["social_media"]["whatsapp"] = item.get("whatsapp", "")
    # print("Structured content:", structured_content)
    return structured_content

def get_content_by_type(db: Database, content_type: str):
    content = db.content.find_one({"type": content_type})
    if content:
        content["id"] = str(content["_id"])
    return content

def create_new_content(db: Database, content):
    # Handle both Pydantic models and dictionaries
    if hasattr(content, 'model_dump'):
        content_dict = content.model_dump()
    else:
        content_dict = content
    
    result = db.content.insert_one(content_dict)
    return str(result.inserted_id)

def update_content_by_id(db: Database, content_id: str, content: ContentCreate):
    result = db.content.update_one(
        {"_id": ObjectId(content_id)}, {"$set": content.model_dump()}
    )
    return result.modified_count > 0

def update_content_by_type(db: Database, content_type: str, content_data: dict):
    print("Updating content for type:", content_type)
    print("Content data:", content_data)
    
    # Remove None values from content_data
    content_data = {k: v for k, v in content_data.items() if v is not None}
    
    # Check if the document exists
    existing_doc = db.content.find_one({"type": content_type})
    print("Existing document:", existing_doc)
    
    if existing_doc:
        # Update existing document
        result = db.content.update_one(
            {"type": content_type}, 
            {"$set": content_data}
        )
        print("Update result:", result.modified_count)
        # Return True if update was successful (even if no changes were made)
        return True
    else:
        # Create new document
        content_data["type"] = content_type
        result = db.content.insert_one(content_data)
        print("Insert result:", result.inserted_id)
        return result.inserted_id is not None

def delete_content_by_id(db: Database, content_id: str):
    result = db.content.delete_one({"_id": ObjectId(content_id)})
    return result.deleted_count > 0 