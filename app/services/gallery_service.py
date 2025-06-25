import os
import shutil
from datetime import datetime
from typing import List, Optional
from pymongo.database import Database
from bson import ObjectId
from app.schemas.gallery import AlbumCreate, AlbumUpdate, ImageCreate, Album, AlbumWithImages
import uuid

def create_album(db: Database, album: AlbumCreate) -> str:
    """Create a new album"""
    album_data = album.model_dump()
    album_data["created_at"] = datetime.utcnow()
    album_data["updated_at"] = datetime.utcnow()
    
    result = db.albums.insert_one(album_data)
    return str(result.inserted_id)

def get_all_albums(db: Database) -> List[Album]:
    """Get all albums with image count and first image"""
    pipeline = [
        {
            "$lookup": {
                "from": "images",
                "localField": "_id",
                "foreignField": "album_id",
                "as": "images"
            }
        },
        {
            "$addFields": {
                "id": { "$toString": "$_id" },
                "image_count": { "$size": "$images" },
                "first_image": { "$arrayElemAt": ["$images", 0] }
            }
        }
    ]
    
    albums_cursor = db.albums.aggregate(pipeline)
    
    albums_list = []
    for album_doc in albums_cursor:
        # The first image is already in the document, we just need to format it
        if album_doc.get("first_image"):
             album_doc["images"] = [album_doc["first_image"]]
        else:
             album_doc["images"] = []
        
        albums_list.append(Album(**album_doc))
    # print("Albums cursor:", albums_list)
    return albums_list

def get_album_by_id(db: Database, album_id: str) -> Optional[AlbumWithImages]:
    """Get album by ID with all images"""
    album = db.albums.find_one({"_id": ObjectId(album_id)})
    if not album:
        return None
    
    album["id"] = str(album["_id"])
    
    # Get all images for this album
    images = list(db.images.find({"album_id": album_id}))
    for image in images:
        image["id"] = str(image["_id"])
    
    album["images"] = images
    album["image_count"] = len(images)
    
    return AlbumWithImages(**album)

def update_album(db: Database, album_id: str, album: AlbumUpdate) -> bool:
    """Update album information"""
    update_data = {k: v for k, v in album.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = db.albums.update_one(
        {"_id": ObjectId(album_id)}, 
        {"$set": update_data}
    )
    return result.modified_count > 0

def delete_album(db: Database, album_id: str) -> bool:
    """Delete album and all its images from storage"""
    # Get all images in the album
    images = list(db.images.find({"album_id": album_id}))
    
    # Delete image files from storage
    for image in images:
        try:
            if os.path.exists(image["file_path"]):
                os.remove(image["file_path"])
        except Exception as e:
            print(f"Error deleting file {image['file_path']}: {e}")
    
    # Delete all images from database
    db.images.delete_many({"album_id": album_id})
    
    # Delete album from database
    result = db.albums.delete_one({"_id": ObjectId(album_id)})
    return result.deleted_count > 0

def upload_image_to_album(db: Database, album_id: str, file, alt_text: Optional[str] = None) -> str:
    """Upload an image to an album"""
    # Check if album exists
    album = db.albums.find_one({"_id": ObjectId(album_id)})
    if not album:
        raise ValueError("Album not found")
    
    # Create unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create album directory if it doesn't exist
    album_dir = os.path.join("media", "gallery", album_id)
    os.makedirs(album_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(album_dir, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create image record
    image_data = {
        "album_id": album_id,
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "mime_type": file.content_type,
        "alt_text": alt_text,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.images.insert_one(image_data)
    return str(result.inserted_id)

def get_image_by_id(db: Database, image_id: str) -> Optional[dict]:
    """Get image by ID"""
    image = db.images.find_one({"_id": ObjectId(image_id)})
    if image:
        image["id"] = str(image["_id"])
    return image

def delete_image(db: Database, image_id: str) -> bool:
    """Delete image from album and storage"""
    image = db.images.find_one({"_id": ObjectId(image_id)})
    if not image:
        return False
    
    # Delete file from storage
    try:
        if os.path.exists(image["file_path"]):
            os.remove(image["file_path"])
    except Exception as e:
        print(f"Error deleting file {image['file_path']}: {e}")
    
    # Delete image record from database
    result = db.images.delete_one({"_id": ObjectId(image_id)})
    return result.deleted_count > 0

def update_image_alt_text(db: Database, image_id: str, alt_text: str) -> bool:
    """Update image alt text"""
    result = db.images.update_one(
        {"_id": ObjectId(image_id)},
        {"$set": {"alt_text": alt_text, "updated_at": datetime.utcnow()}}
    )
    return result.modified_count > 0 