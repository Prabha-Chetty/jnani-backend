from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from app.schemas.contact_enquiry import ContactEnquiryCreate, ContactEnquiryUpdate, ContactEnquiry
from app.services.contact_enquiry_service import (
    create_contact_enquiry,
    get_all_contact_enquiries,
    get_contact_enquiry_by_id,
    update_contact_enquiry,
    delete_contact_enquiry,
    get_contact_enquiries_count
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

public_router = APIRouter()
admin_router = APIRouter()

@public_router.post("/", response_model=dict)
async def submit_contact_enquiry(
    enquiry_data: ContactEnquiryCreate,
    db: Database = Depends(get_database)
):
    """Submit a new contact enquiry"""
    try:
        enquiry_id = create_contact_enquiry(db, enquiry_data)
        return {
            "message": "Contact enquiry submitted successfully",
            "id": enquiry_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to submit enquiry")

@admin_router.get("/", response_model=List[ContactEnquiry])
async def get_contact_enquiries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all contact enquiries (admin only)"""
    enquiries = get_all_contact_enquiries(db, skip, limit)
    return enquiries

@admin_router.get("/{enquiry_id}", response_model=ContactEnquiry)
async def get_contact_enquiry(
    enquiry_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get contact enquiry by ID (admin only)"""
    enquiry = get_contact_enquiry_by_id(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Contact enquiry not found")
    return enquiry

@admin_router.put("/{enquiry_id}", response_model=dict)
async def update_enquiry(
    enquiry_id: str,
    update_data: ContactEnquiryUpdate,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update contact enquiry status and notes (admin only)"""
    success = update_contact_enquiry(db, enquiry_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Contact enquiry not found")
    
    return {"message": "Contact enquiry updated successfully"}

@admin_router.delete("/{enquiry_id}", response_model=dict)
async def delete_enquiry(
    enquiry_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete contact enquiry (admin only)"""
    success = delete_contact_enquiry(db, enquiry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact enquiry not found")
    
    return {"message": "Contact enquiry deleted successfully"}

@admin_router.get("/stats/counts", response_model=dict)
async def get_enquiry_counts(
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get contact enquiry counts by status (admin only)"""
    counts = get_contact_enquiries_count(db)
    return counts 