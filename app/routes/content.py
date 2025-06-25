from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List
from app.schemas.content import (
    ContentUpdate, 
    AboutContentUpdate, 
    ContactContentUpdate, 
    SocialMediaContentUpdate
)
from app.services.content_service import (
    get_content_by_type,
    update_content_by_type,
    get_all_content
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

public_router = APIRouter()
admin_router = APIRouter()

@public_router.get("/", response_model=Any)
async def get_public_content(db: Database = Depends(get_database)):
    """
    This endpoint fetches all combined content (about, contact, social) 
    for the public-facing website.
    """
    # content_data = get_content_by_type(db, "main_content")
    content_data = get_all_content(db)
    # print(content_data)
    # return content_data
    if not content_data:
        # If no content exists, create a default one
        default_content = {
            "about_us": "Welcome to Jnani Study Center.",
            "contact_us": {
                "mobile": "",
                "address": ""
            },
            "map_link": "https://maps.google.com",
            "social_media": {
                "facebook": "",
                "youtube": ""
            }
        }
        # from app.services.content_service import create_new_content
        # content_id = create_new_content(db, {"content_type": "main_content", "data": default_content})
        # content_data = get_content_by_type(db, "main_content")

    if not content_data:
        raise HTTPException(status_code=404, detail="Content not found")
        
    return content_data

@admin_router.get("/{content_type}", response_model=Any)
async def get_admin_content(
    content_type: str,
    db: Database = Depends(get_database)
    # current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Get all content and filter by type
    all_content = get_all_content(db)
    
    # Extract the specific content type from the structured data
    if content_type == "about":
        content_data = {
            "description": all_content.get("about_us", ""),
            "mission": all_content.get("mission", ""),
            "vision": all_content.get("vision", ""),
            "values": all_content.get("values", [])
        }
    elif content_type == "contact":
        contact_us = all_content.get("contact_us", {})
        content_data = {
            "phone": contact_us.get("phone", ""),
            "address": contact_us.get("address", ""),
            "map_link": all_content.get("map_link", "")
        }
    elif content_type == "social_media":
        social_media = all_content.get("social_media", {})
        content_data = {
            "facebook": social_media.get("facebook", ""),
            "youtube": social_media.get("youtube", ""),
            "instagram": social_media.get("instagram", ""),
            "twitter": social_media.get("twitter", ""),
            "linkedin": social_media.get("linkedin", ""),
            "whatsapp": social_media.get("whatsapp", "")
        }
    else:
        raise HTTPException(status_code=404, detail="Content type not found")
    
    return content_data

@admin_router.put("/{content_type}", response_model=dict)
async def update_content(
    content_type: str,
    request: Request,
    db: Database = Depends(get_database),
    # current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Get the request body
        body = await request.json()
        
        # Validate the content based on content_type
        if content_type == "about":
            content = AboutContentUpdate(**body)
        elif content_type == "contact":
            content = ContactContentUpdate(**body)
        elif content_type == "social_media":
            content = SocialMediaContentUpdate(**body)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        print("Validated content:", content)
        
        # Update or create the content
        success = update_content_by_type(db, content_type, content.model_dump(exclude_unset=True))
        
        if success:
            return {"message": "Content updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update content")
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid content data: {str(e)}") 