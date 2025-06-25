from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from app.schemas.gallery import Album, AlbumCreate, AlbumUpdate, AlbumWithImages, Image
from app.services.gallery_service import (
    create_album,
    get_all_albums,
    get_album_by_id,
    update_album,
    delete_album,
    upload_image_to_album,
    get_image_by_id,
    delete_image,
    update_image_alt_text
)
from app.db.database import get_database
from app.services.auth import get_current_user
from pymongo.database import Database

router = APIRouter()

@router.get("/albums", response_model=List[Album], response_model_by_alias=False)
async def get_albums(db: Database = Depends(get_database)):
    """Get all albums"""
    return get_all_albums(db)

@router.get("/albums/{album_id}", response_model=AlbumWithImages, response_model_by_alias=False)
async def get_album(album_id: str, db: Database = Depends(get_database)):
    """Get album by ID with all images"""
    album = get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album

@router.post("/albums", response_model=dict)
async def create_new_album(
    album: AlbumCreate,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new album"""
    album_id = create_album(db, album)
    return {"message": "Album created successfully", "id": album_id}

@router.put("/albums/{album_id}", response_model=dict)
async def update_album_info(
    album_id: str,
    album: AlbumUpdate,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update album information"""
    success = update_album(db, album_id, album)
    if not success:
        raise HTTPException(status_code=404, detail="Album not found")
    return {"message": "Album updated successfully"}

@router.delete("/albums/{album_id}", response_model=dict)
async def delete_album_complete(
    album_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete album and all its images"""
    success = delete_album(db, album_id)
    if not success:
        raise HTTPException(status_code=404, detail="Album not found")
    return {"message": "Album and all images deleted successfully"}

@router.post("/albums/{album_id}/images", response_model=dict)
async def upload_image(
    album_id: str,
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Upload image to album"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 10MB")
    
    try:
        image_id = upload_image_to_album(db, album_id, file, alt_text)
        return {"message": "Image uploaded successfully", "id": image_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image")

@router.get("/images/{image_id}", response_model=Image)
async def get_image(image_id: str, db: Database = Depends(get_database)):
    """Get image by ID"""
    image = get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.delete("/images/{image_id}", response_model=dict)
async def delete_single_image(
    image_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete image from album and storage"""
    success = delete_image(db, image_id)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}

@router.put("/images/{image_id}/alt-text", response_model=dict)
async def update_image_alt(
    image_id: str,
    alt_text: str = Form(...),
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update image alt text"""
    success = update_image_alt_text(db, image_id, alt_text)
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image alt text updated successfully"} 