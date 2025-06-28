from pydantic import BaseModel, Field, computed_field, model_validator
from typing import List, Optional
from datetime import datetime
from .py_object_id import PyObjectId

class ImageBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    alt_text: Optional[str] = None

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: str
    album_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlbumBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    is_active: bool = True

class AlbumCreate(AlbumBase):
    pass

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AlbumImage(BaseModel):
    id: str
    file_path: str
    alt_text: Optional[str] = None
    uploaded_at: datetime = Field(..., alias="created_at")

    @model_validator(mode='after')
    def build_full_url(self):
        if self.file_path and not self.file_path.startswith('http'):
            self.file_path = f"https://jnani-backend.onrender.com/{self.file_path}"
        return self

    class Config:
        populate_by_name = True
        from_attributes = True

class Album(AlbumBase):
    id: PyObjectId = Field(..., alias="_id")
    images: List[AlbumImage] = []
    image_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True

class AlbumWithImages(AlbumBase):
    id: PyObjectId = Field(..., alias="_id")
    images: List[AlbumImage] = []
    image_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True 