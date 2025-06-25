from pydantic import BaseModel, Field
from typing import Optional

class ClassBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = None

class ClassCreate(ClassBase):
    pass

class ClassUpdate(ClassBase):
    pass

class Class(ClassBase):
    id: str

    class Config:
        from_attributes = True 