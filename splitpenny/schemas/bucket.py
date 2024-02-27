from pydantic import BaseModel
from datetime import datetime

class BucketBase(BaseModel):
    title: str
    description: str
    owner_id: int
    
class BucketInSchema(BucketBase):
    
    class Config:
        from_attributes = True
        
class BucketOutSchema(BucketBase):
    id: int
    
    class Config:
        from_attributes = True
    
