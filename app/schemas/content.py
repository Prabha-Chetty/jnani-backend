from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Union
from .py_object_id import PyObjectId

class ContentBase(BaseModel):
    title: str
    content: str
    type: str  # about, contact, social_media
    is_active: bool = True

class AboutContent(BaseModel):
    title: str
    description: str
    mission: str
    vision: str
    values: List[str]

class ContactContent(BaseModel):
    phone: str
    email: str
    address: str
    map_link: str
    working_hours: str

class SocialMediaContent(BaseModel):
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    youtube: Optional[str] = None
    whatsapp: Optional[str] = None

class SocialMediaLink(BaseModel):
    platform: str
    url: HttpUrl

class ContentCreate(ContentBase):
    pass

class Content(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    about_us: str
    contact_us: str
    map_link: Optional[HttpUrl] = None
    social_media: List[SocialMediaLink] = []

    class Config:
        populate_by_name = True
        from_attributes = True

# Update models for different content types
class AboutContentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: Optional[List[str]] = None

class ContactContentUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    map_link: Optional[str] = None
    working_hours: Optional[str] = None

class SocialMediaContentUpdate(BaseModel):
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    youtube: Optional[str] = None
    whatsapp: Optional[str] = None

# Union type for ContentUpdate
ContentUpdate = Union[AboutContentUpdate, ContactContentUpdate, SocialMediaContentUpdate] 