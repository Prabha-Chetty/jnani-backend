from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
import json
from datetime import datetime
from app.schemas.event import Event, EventCreate, EventUpdate
from app.services.event_service import (
    get_all_events,
    create_new_event,
    update_event_by_id,
    delete_event_by_id,
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

def event_from_json(event_json: str = Form(...)) -> EventCreate:
    try:
        data = json.loads(event_json)
        data['event_date'] = datetime.fromisoformat(data['event_date'])
        return EventCreate(**data)
    except (json.JSONDecodeError, KeyError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid JSON format for event data")

@router.get("/", response_model=List[Event])
async def read_events(
    db: Database = Depends(get_database)
):
    return get_all_events(db)

@router.get("/carousel", response_model=List[dict])
async def get_carousel_images(
    db: Database = Depends(get_database)
):
    """
    Get images from active events for carousel display
    """
    events = get_all_events(db)
    carousel_items = []
    
    for event in events:
        if event.get("is_active", True) and event.get("image_url"):
            carousel_items.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "image_url": event.get("image_url")
            })
    
    return carousel_items

@router.get("/section", response_model=List[dict])
async def get_events_section(
    db: Database = Depends(get_database)
):
    """
    Get events with videos for the events section
    """
    events = get_all_events(db)
    section_events = []
    
    for event in events:
        if event.get("is_active", True):
            section_events.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "event_date": event.get("event_date"),
                "image_url": event.get("image_url"),
                "video_url": event.get("video_url")
            })
    
    return section_events

@router.post("/", response_model=dict)
async def create_event(
    event: EventCreate = Depends(event_from_json),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    event_id = create_new_event(db, event, image, video)
    return {"message": "Event created successfully", "id": event_id}

@router.put("/{event_id}", response_model=dict)
async def update_event(
    event_id: str,
    event: EventUpdate = Depends(event_from_json),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not update_event_by_id(db, event_id, event, image, video):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated successfully"}

@router.delete("/{event_id}", response_model=dict)
async def delete_event(
    event_id: str, 
    db: Database = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    if not delete_event_by_id(db, event_id):
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"} 