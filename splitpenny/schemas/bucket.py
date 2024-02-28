from pydantic import BaseModel
from datetime import datetime

class BucketBase(BaseModel):
    title: str
    description: str  
    
class BucketCreateSchema(BucketBase):
    owner_id: int
    
    class Config:
        from_attributes = True
        
class BucketOutSchema(BucketBase):
    id: int
    members_id: list[int] = []
    owner_id: int
    
    class Config:
        from_attributes = True
    
