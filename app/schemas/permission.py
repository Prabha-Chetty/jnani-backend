from pydantic import BaseModel, Field
from typing import Optional, List
from .py_object_id import PyObjectId

class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True 