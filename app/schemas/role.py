from pydantic import BaseModel, Field
from typing import List, Optional
from .py_object_id import PyObjectId

class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    permissions: List[str] = []

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        from_attributes = True 