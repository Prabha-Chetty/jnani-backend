from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime

class LibraryItemBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    file_url: Optional[str] = None

class LibraryItem(LibraryItemBase):
    id: str
    
    @model_validator(mode='after')
    def build_full_url(self):
        if self.file_url and not self.file_url.startswith('http'):
            self.file_url = f"http://localhost:8000{self.file_url}"
        return self

    class Config:
        populate_by_name = True
        from_attributes = True

class LibraryItemCreate(LibraryItemBase):
    pass

class LibraryItemUpdate(LibraryItemBase):
    pass 