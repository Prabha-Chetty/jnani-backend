from typing import List, Optional
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
from app.schemas.contact_enquiry import ContactEnquiryCreate, ContactEnquiryUpdate

def create_contact_enquiry(db: Database, enquiry_data: ContactEnquiryCreate) -> str:
    """Create a new contact enquiry"""
    enquiry_dict = enquiry_data.model_dump()
    enquiry_dict["status"] = "pending"
    enquiry_dict["created_at"] = datetime.utcnow()
    enquiry_dict["updated_at"] = datetime.utcnow()
    
    result = db.contact_enquiries.insert_one(enquiry_dict)
    return str(result.inserted_id)

def get_all_contact_enquiries(db: Database, skip: int = 0, limit: int = 100) -> List[dict]:
    """Get all contact enquiries with pagination"""
    enquiries = list(db.contact_enquiries.find().sort("created_at", -1).skip(skip).limit(limit))
    
    for enquiry in enquiries:
        enquiry["id"] = str(enquiry["_id"])
    
    return enquiries

def get_contact_enquiry_by_id(db: Database, enquiry_id: str) -> Optional[dict]:
    """Get contact enquiry by ID"""
    enquiry = db.contact_enquiries.find_one({"_id": ObjectId(enquiry_id)})
    
    if enquiry:
        enquiry["id"] = str(enquiry["_id"])
    
    return enquiry

def update_contact_enquiry(db: Database, enquiry_id: str, update_data: ContactEnquiryUpdate) -> bool:
    """Update contact enquiry status and notes"""
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    result = db.contact_enquiries.update_one(
        {"_id": ObjectId(enquiry_id)},
        {"$set": update_dict}
    )
    
    return result.modified_count > 0

def delete_contact_enquiry(db: Database, enquiry_id: str) -> bool:
    """Delete contact enquiry"""
    result = db.contact_enquiries.delete_one({"_id": ObjectId(enquiry_id)})
    return result.deleted_count > 0

def get_contact_enquiries_count(db: Database) -> dict:
    """Get count of enquiries by status"""
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }
        }
    ]
    
    results = list(db.contact_enquiries.aggregate(pipeline))
    counts = {"total": 0, "pending": 0, "read": 0, "replied": 0, "closed": 0}
    
    for result in results:
        status = result["_id"]
        count = result["count"]
        counts[status] = count
        counts["total"] += count
    
    return counts 