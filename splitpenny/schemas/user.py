from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str
    full_name: str
    is_active: bool | None
    telegram_id: int | None
    telegram_username: str | None
    
class UserInSchema(UserBase):
    password : str = Field(..., max_length=128)
    
    class Config:
        from_attributes = True
        
class UserOutSchema(UserBase):
    id: int
    
    class Config:
        from_attributes = True
        
class UserDatabaseSchema(UserBase):
    created_at: datetime
    modified_at: datetime
    
    class Config:
        from_attributes = True