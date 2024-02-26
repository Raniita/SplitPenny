from pydantic import BaseModel, Field
from datetime import datetime

class UserInSchema(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., max_length=20)
    full_name: str | None = Field(..., max_length=50)
    password : str = Field(..., max_length=128)
    is_active: bool | None = True
    telegram_id : int | None = None
    telegram_username: str | None = Field(None, max_length=50)
    
    class Config:
        orm_mode = True
        
class UserOutSchema(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    is_active: bool
    telegram_id: int | None
    telergam_username: str | None
    modified_at: datetime
    
    class Config:
        orm_mode = True
        
class UserDatabaseSchema(BaseModel):
    id: int
    email: str
    username: str
    full_name: str | None
    password: str
    is_active: bool
    telegram_id: int | None
    telegram_username: str | None
    created_at: datetime
    modified_at: datetime
    
    class Config:
        orm_mode = True