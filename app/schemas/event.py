from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from .py_object_id import PyObjectId

class EventBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    event_date: datetime
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class Event(EventBase):
    id: PyObjectId = Field(..., alias="_id")

    @model_validator(mode='after')
    def build_full_urls(self):
        if self.image_url and not self.image_url.startswith('http'):
            self.image_url = f"http://localhost:8000/{self.image_url}"
        
        if self.video_url and not self.video_url.startswith('http'):
            self.video_url = f"http://localhost:8000/{self.video_url}"
        
        return self

    class Config:
        populate_by_name = True
        from_attributes = True

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass 