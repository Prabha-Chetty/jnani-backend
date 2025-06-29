from pymongo.database import Database
from app.schemas.event import EventCreate, EventUpdate
from bson import ObjectId
from fastapi import UploadFile
import shutil
import os
from typing import Optional
from app.config import settings

MEDIA_DIR = "media"

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

def get_all_events(db: Database):
    events = list(db.events.find())
    for event in events:
        event["id"] = str(event["_id"])
        if event.get("image_url"):
            event["image_url"] = f"{settings.MEDIA_URL}{event['image_url']}"
        if event.get("video_url"):
            event["video_url"] = f"{settings.MEDIA_URL}{event['video_url']}"
    return events

def create_new_event(db: Database, event: EventCreate, image: Optional[UploadFile] = None, video: Optional[UploadFile] = None):
    event_dict = event.dict()
    
    if image:
        image_location = os.path.join(MEDIA_DIR, image.filename)
        save_upload_file(image, image_location)
        event_dict["image_url"] = f"/media/{image.filename}"
    
    if video:
        video_location = os.path.join(MEDIA_DIR, video.filename)
        save_upload_file(video, video_location)
        event_dict["video_url"] = f"/media/{video.filename}"

    result = db.events.insert_one(event_dict)
    return str(result.inserted_id)

def update_event_by_id(db: Database, event_id: str, event: EventUpdate, image: Optional[UploadFile] = None, video: Optional[UploadFile] = None):
    event_dict = event.dict(exclude_unset=True)
    
    old_event = db.events.find_one({"_id": ObjectId(event_id)})

    if image:
        if old_event and old_event.get("image_url"):
            old_image_path = old_event["image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        image_location = os.path.join(MEDIA_DIR, image.filename)
        save_upload_file(image, image_location)
        event_dict["image_url"] = f"/media/{image.filename}"

    if video:
        if old_event and old_event.get("video_url"):
            old_video_path = old_event["video_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(old_video_path):
                os.remove(old_video_path)

        video_location = os.path.join(MEDIA_DIR, video.filename)
        save_upload_file(video, video_location)
        event_dict["video_url"] = f"/media/{video.filename}"
    
    result = db.events.update_one(
        {"_id": ObjectId(event_id)}, {"$set": event_dict}
    )
    return result.modified_count > 0

def delete_event_by_id(db: Database, event_id: str):
    event = db.events.find_one({"_id": ObjectId(event_id)})
    if event:
        if event.get("image_url"):
            image_path = event["image_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(image_path):
                os.remove(image_path)
        if event.get("video_url"):
            video_path = event["video_url"].replace("/media/", f"{MEDIA_DIR}/", 1)
            if os.path.exists(video_path):
                os.remove(video_path)
            
    result = db.events.delete_one({"_id": ObjectId(event_id)})
    return result.deleted_count > 0 